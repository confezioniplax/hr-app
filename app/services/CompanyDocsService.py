from __future__ import annotations
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import date
import re

from fastapi.encoders import jsonable_encoder
from app.settings import get_settings
from app.repo.CompanyDocsRepository import CompanyDocsRepository


class CompanyDocsService:
    """
    Gestione Documenti Aziendali (organigramma, verbali, sorveglianze, ecc.)
    - Salvataggio file su disco
    - Naming: <titolo_sanitizzato>_<anno>.<ext> in /DocumentiAziendali/<categoria_code>/<anno>/
    - Se il file esiste, aggiunge suffisso __1, __2, ...
    """

    def __init__(self):
        self.repo = CompanyDocsRepository()

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
        category: str,              # 👈 deve essere IL CODE (es. 'ORG', 'DVR', 'ALTRO')
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
