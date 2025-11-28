from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import date
import re
import io

from fastapi.encoders import jsonable_encoder
from app.settings import get_settings
from app.repo.CompanyDocsRepository import CompanyDocsRepository

# AI / PDF
from pypdf import PdfReader  # assicurati di avere pypdf in requirements
from app.services.AISuggestionService import AISuggestionService


class CompanyDocsService:
    """
    Gestione Documenti Aziendali (organigramma, verbali, sorveglianze, ecc.)
    - Salvataggio file su disco
    - Naming: <titolo_sanitizzato>_<anno>.<ext> in /DocumentiAziendali/<categoria_code>/<anno>/
    - Se il file esiste, aggiunge suffisso __1, __2, ...
    """

    def __init__(self):
        self.repo = CompanyDocsRepository()
        # AI opzionale: se manca configurazione o Groq non è settato, non blocco il resto
        try:
            self.ai = AISuggestionService()
        except Exception:
            self.ai = None

    # -------- LISTA --------
    def list_docs(
        self,
        q: Optional[str] = None,
        year: Optional[int] = None,
        frequency: Optional[str] = None,
        category_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows = self.repo.list_docs(
            q=q,
            year=year,
            frequency=frequency,
            category_code=category_code,
        )
        return self._encode(rows)

    # -------- CATEGORIE (per UI) --------
    def list_categories(self) -> List[Dict[str, Any]]:
        """
        Ritorna le categorie da company_doc_categories:
        - code
        - label
        - sort_order
        """
        rows = self.repo.list_categories()
        return self._encode(rows)

    # -------- GET --------
    def get_doc(self, doc_id: int) -> Optional[Dict[str, Any]]:
        row = self.repo.get_doc(doc_id)
        return self._encode(row) if row else None

    # -------- UPSERT --------
    def upsert_doc(
        self,
        *,
        id: Optional[int],
        title: str,
        year: int,
        category: str,              # 👈 deve essere IL CODE (es. 'VAL_RISCHI', 'ASS', 'IMPIANTI_MAC')
        frequency: str,
        notes: Optional[str],
        file_bytes: Optional[bytes],
        original_filename: Optional[str],
    ) -> int:
        """
        Se arriva un file, lo salva su disco e passa il file_path al repository.
        Se non arriva file in update, il file_path resta invariato (gestito dal repo).
        """
        # 1) normalizza campi base
        title = (title or "").strip()
        if not title:
            raise ValueError("Titolo documento obbligatorio")

        # category = code FK su company_doc_categories.code
        category_code = (category or "").strip().upper() or "ALTRO"
        frequency = (frequency or "annuale").strip()
        notes = (notes or None)

        # (opzionale ma sano) validazione contro le categorie note
        valid_codes = {c["code"] for c in self.repo.list_categories()}
        if category_code not in valid_codes:
            raise ValueError(f"Categoria non valida: {category_code}")

        # 2) salva l'allegato (se presente)
        file_path: Optional[str] = None
        if file_bytes and original_filename:
            file_path = self._save_attachment(
                title=title,
                year=int(year),
                category_code=category_code,
                original_filename=original_filename,
                content=file_bytes,
            )

        # 3) delega al repo l'upsert
        return int(
            self.repo.upsert_doc(
                id=id,
                title=title,
                year=int(year),
                category=category_code,
                frequency=frequency,
                notes=notes,
                file_path=file_path,  # None => non modificare
            )
        )

    # -------- DELETE --------
    def delete_doc(self, doc_id: int) -> None:
        # per sicurezza NON cancelliamo il file fisico (storico), solo il record
        self.repo.delete_doc(doc_id)

    # =======================
    #  AI: SUGGERIMENTO METADATI
    # =======================
    def suggest_metadata_from_file(
        self,
        *,
        title: str,
        file_bytes: bytes,
        original_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Usa l'AI (se configurata) per proporre:
        - category (code)
        - frequency
        - year

        NON tocca il DB. È solo un assist per la UI.
        """
        # se l'AI non è disponibile (chiave mancante ecc.), non blocchiamo
        if not self.ai:
            return {"category": None, "frequency": None, "year": None}

        title = (title or "").strip()
        filename = (original_filename or "").strip()

        # Estrai testo dal PDF, con fallback OCR sui casi "scansione"
        if file_bytes:
            fname_lower = filename.lower()
            if fname_lower.endswith(".pdf"):
                pdf_text = self._extract_text_from_pdf_bytes(file_bytes)
            else:
                # Non-PDF: per ora non estraiamo, ma passiamo comunque filename al modello
                pdf_text = ""
        else:
            pdf_text = ""

        # Inserisco anche il nome file nel testo passato all'AI,
        # così le regole Heuristiche vedono pattern tipo MUD_2024_2025 ecc.
        combined_text_parts: List[str] = []
        if filename:
            combined_text_parts.append(f"NOME_FILE: {filename}")
        if pdf_text:
            combined_text_parts.append(pdf_text)

        text_for_ai = "\n\n".join(combined_text_parts)

        suggestions = self.ai.suggest_doc_metadata(title=title, text=text_for_ai)

        # validazione vs categorie reali del DB
        categories = self.repo.list_categories()
        valid_codes = {(c["code"] or "").upper() for c in categories}

        cat = suggestions.get("category")
        if cat:
            cat = str(cat).strip().upper()
            if cat not in valid_codes:
                # fallback furbo: se esiste ALTRO, usiamo quello, altrimenti None
                if "ALTRO" in valid_codes:
                    cat = "ALTRO"
                else:
                    cat = None
        else:
            cat = None

        freq = suggestions.get("frequency")
        if freq:
            freq = str(freq).strip().lower()
        else:
            freq = None

        # Frequenze reali che usi TU:
        valid_freq = {
            "annuale",
            "semestrale",
            "biennale",
            "triennale",
            "quadriennale",
            "quinquennale",
            "una_tantum",
            "variabile",
        }
        if freq not in valid_freq:
            freq = None

        year = suggestions.get("year")
        try:
            year = int(year) if year is not None else None
        except Exception:
            year = None

        return {
            "category": cat,
            "frequency": freq,
            "year": year,
        }

    # =======================
    # Helpers
    # =======================
    def _encode(self, obj: Any) -> Any:
        return jsonable_encoder(obj)

    def _safe_chunk(self, s: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", (s or "").strip())

    def _base_docs_root(self) -> Path:
        """
        Usa DOCS_BASE_DIR se presente nelle settings, altrimenti ricade su CERTS_BASE_DIR.
        Dentro quel root usa la cartella 'DocumentiAziendali'.
        """
        settings = get_settings()
        base = getattr(settings, "DOCS_BASE_DIR", None) or settings.CERTS_BASE_DIR
        return Path(base) / "DocumentiAziendali"

    def _build_dest_path(
        self,
        *,
        title: str,
        year: int,
        category_code: str,
        original_filename: str,
    ) -> Path:
        """
        Path finale:
            <BASE>/DocumentiAziendali/<CATEGORY_CODE>/<YEAR>/<titolo>_<anno>.<ext>
        """
        root = self._base_docs_root()
        cat = self._safe_chunk(category_code or "ALTRO")
        yr = str(int(year))

        ext = ""
        name = (original_filename or "").strip()
        if "." in name:
            ext = "." + name.split(".")[-1].lower()

        fname = f"{self._safe_chunk(title)}_{yr}{ext}"
        dest_dir = root / cat / yr
        dest_dir.mkdir(parents=True, exist_ok=True)
        return dest_dir / fname

    def _save_attachment(
        self,
        *,
        title: str,
        year: int,
        category_code: str,
        original_filename: str,
        content: bytes,
    ) -> str:
        """
        Salva fisicamente il file e ritorna il path stringa.
        Gestisce il suffisso __1, __2, ... se già esiste un file con lo stesso nome.
        """
        dest = self._build_dest_path(
            title=title,
            year=year,
            category_code=category_code,
            original_filename=original_filename,
        )
        candidate = dest
        i = 1
        while candidate.exists():
            candidate = dest.with_stem(f"{dest.stem}__{i}")
            i += 1
        candidate.write_bytes(content)
        return str(candidate)

    def _extract_text_from_pdf_bytes(self, file_bytes: bytes) -> str:
        """
        Estrae testo da PDF:
        1) tenta pypdf (testo "vero")
        2) se viene vuoto, prova OCR pagina per pagina (se librerie OCR presenti)
        3) se anche OCR non è disponibile/funziona, ritorna stringa vuota

        Non lancia eccezioni verso l'alto: peggio dei casi, l'AI vedrà solo il titolo/nome file.
        """
        if not file_bytes:
            return ""

        # --- step 1: pypdf ---
        text_chunks: List[str] = []
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                try:
                    t = page.extract_text() or ""
                except Exception:
                    t = ""
                if t:
                    text_chunks.append(t)
        except Exception:
            # se il PDF è rotto, saltiamo direttamente a OCR (se possibile)
            text_chunks = []

        full_text = "\n\n".join(text_chunks).strip()
        if full_text:
            return full_text

        # --- step 2: OCR opzionale ---
        # qui NON ci facciamo esplodere se mancano le librerie
        try:
            # PyMuPDF
            import fitz  # type: ignore
            from PIL import Image  # type: ignore
            import pytesseract  # type: ignore
        except Exception:
            # niente OCR disponibile
            return ""

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception:
            return ""

        ocr_chunks: List[str] = []
        try:
            for page in doc:
                try:
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_bytes))
                    txt = pytesseract.image_to_string(img, lang="ita")
                    if txt:
                        ocr_chunks.append(txt)
                except Exception:
                    # se una pagina fallisce, ne proviamo le altre
                    continue
        finally:
            doc.close()

        return "\n\n".join(ocr_chunks).strip()
