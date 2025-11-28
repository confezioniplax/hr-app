"""
AISuggestionService
- Usa Groq (Llama 3.1 8B) per suggerire:
  - category (code categoria, es. VAL_RISCHI, IMPIANTI_MAC, ASS, ATM, MODULI, NOMINE, ecc.)
  - frequency (annuale/semestrale/biennale/triennale/quadriennale/quinquennale/una_tantum/variabile)
  - year (anno int)
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

from groq import Groq
from app.settings import get_settings

logger = logging.getLogger(__name__)


# Codici categoria che usi realmente nei tuoi company_docs
VALID_CATEGORIES = {
    "INF_GEN",
    "NOMINE",
    "FORM_ADESTR",
    "VAL_RISCHI",
    "MODULI",
    "IMPIANTI_MAC",
    "EMERGENZA",
    "SORV_SAN",
    "INQ",
    "RIF",
    "SAS",
    "ASS",
    "ATM",
    "QUAL",
    "LEG",
    "VARIE",
}

# Frequenze effettivamente usate
VALID_FREQUENCIES = {
    "annuale",
    "semestrale",
    "biennale",
    "triennale",
    "quadriennale",
    "quinquennale",
    "una_tantum",
    "variabile",
}


def _normalize_text(s: Optional[str]) -> str:
    """
    Normalizza stringa per i match:
    - lowercase
    - '_' e '-' → spazio
    - rimozione estensione file
    - spazi compressi
    """
    if not s:
        return ""
    s = s.lower().replace("_", " ").replace("-", " ")
    s = re.sub(r"\.(pdf|docx?|xlsx?|jpg|jpeg|png)$", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _extract_year(*chunks: str) -> Optional[int]:
    """
    Cerca pattern 20xx nei pezzi forniti e ritorna l'anno più recente.
    Se non trova nulla, ritorna None.
    """
    text = " ".join(c for c in chunks if c)
    matches = re.findall(r"\b(20[0-9]{2})\b", text)
    if not matches:
        return None
    try:
        years = [int(m) for m in matches]
        return max(years)
    except Exception:
        return None


def _heuristic_category_frequency_from_text(norm_text: str) -> Dict[str, Optional[str]]:
    """
    Heuristics 'secche' basate su titolo+testo normalizzati.
    Ritorna {category, frequency}, senza year.
    Tenta di riprodurre quello che hai già messo a mano nei tuoi company_docs.
    """
    t = f" {norm_text} "  # spazi ai lati per match più semplici

    # --- REGOLA FORTE: PRIMO/PRONTO SOCCORSO ---
    # Qui non vogliamo discutere con il modello: normativamente è triennale.
    if "primo soccorso" in t or "pronto soccorso" in t:
        # Se è chiaramente una nomina (Nom8, parola "nomina"), vai su NOMINE triennale
        if " nom8 " in t or "nom8 " in t or " nom 8 " in t or " nomina " in t:
            return {"category": "NOMINE", "frequency": "triennale"}
        # Se appare in moduli/formazione, tieni comunque triennale
        if " modulo " in t or " moduli " in t or "formazione" in t or "addestramento" in t:
            return {"category": "FORM_ADESTR", "frequency": "triennale"}
        # Default prudente: nomina primo soccorso triennale
        return {"category": "NOMINE", "frequency": "triennale"}

    # --- SORVEGLIANZA SANITARIA / REGISTRO INFORTUNI ---
    if "sorveglianza sanitaria" in t or "adempimenti in materia di sorveglianza sanitaria" in t:
        return {"category": "SORV_SAN", "frequency": "annuale"}

    if "registro infortuni" in t:
        # nei tuoi dati è VAL_RISCHI, annuale
        return {"category": "VAL_RISCHI", "frequency": "annuale"}

    # --- FORMAZIONE / ADDESTRAMENTO ---
    if "aggiornamento formazione lavoratori" in t:
        return {"category": "FORM_ADESTR", "frequency": "quinquennale"}
    if "formazione lavoratori" in t or "addestramento" in t or "moduli plax addestramento" in t:
        return {"category": "FORM_ADESTR", "frequency": "quinquennale"}

    # --- MODULI operativi (DPI, APS, AAI, Mulettisti, NomX_...) ---
    if " modulo " in t or " moduli " in t:
        # mulettisti, APS, AAI, Dalmec → MODULI con frequenze varie
        if "mulettisti" in t or " nom10 " in t:
            return {"category": "MODULI", "frequency": "quinquennale"}
        if "preposto" in t or " nom6 " in t:
            return {"category": "MODULI", "frequency": "biennale"}
        if " aps " in t or " aai " in t:
            return {"category": "MODULI", "frequency": "quinquennale"}
        if "manutenzione dalmec" in t or "manutenzioni dalmec" in t or "manutenzionidalmec" in t:
            return {"category": "MODULI", "frequency": "variabile"}
        # default modulo generico
        return {"category": "MODULI", "frequency": "variabile"}

    # --- NOMINE (NOM1, NOM2, NOM7, NOM8 ecc.) ---
    if " nom1 " in t or " nom2 " in t or " nom7 " in t or " nom8 " in t or " nom6 " in t \
       or "nomina addetti antincendio" in t or "nomina addetti primo soccorso" in t \
       or "svolgimento diretto dei compiti di prevenzione e protezione" in t \
       or "svolg diretto 81" in t:
        if "primo soccorso" in t or "pronto soccorso" in t:
            return {"category": "NOMINE", "frequency": "triennale"}
        if "antincendio" in t:
            return {"category": "NOMINE", "frequency": "quinquennale"}
        if "rappresentante dei lavoratori per la sicurezza" in t or " rls " in t:
            return {"category": "NOMINE", "frequency": "quinquennale"}
        if "svolgimento diretto" in t or "svolg diretto" in t:
            return {"category": "NOMINE", "frequency": "quinquennale"}
        return {"category": "NOMINE", "frequency": "quinquennale"}

    # --- ASSICURAZIONI / POLIZZE ---
    if " polizza " in t or t.strip().startswith("polizza ") or "assicurativa" in t:
        return {"category": "ASS", "frequency": "annuale"}

    # --- RIFIUTI / MUD / CONAI ---
    if " mud " in t or t.strip().startswith("mud ") or " mud " in t:
        return {"category": "RIF", "frequency": "annuale"}
    if " conai" in t:
        # nei tuoi dati → INF_GEN, variabile.
        return {"category": "INF_GEN", "frequency": "variabile"}

    # --- ATM / AUA / Solventi ---
    if "autorizzazione unica ambientale" in t or " aua " in t or t.strip().startswith("atm"):
        if "piano di gestione dei solventi" in t:
            return {"category": "ATM", "frequency": "annuale"}
        return {"category": "ATM", "frequency": "una_tantum"}

    # --- EMERGENZA: prove evacuazione ---
    if "prove evacuazione" in t or "prova evacuazione" in t:
        return {"category": "EMERGENZA", "frequency": "annuale"}

    # --- VERBALE RIUNIONE PERIODICA ---
    if "verbale riunione periodica" in t:
        return {"category": "VAL_RISCHI", "frequency": "annuale"}

    # --- VALUTAZIONI RISCHIO (chimico, rumore, vibrazioni, campi elettrici, MMC, civico) ---
    if "documento valutazione del rischio civico" in t or "documento valutazione del rischio" in t:
        # nei tuoi dati: VAL_RISCHI, variabile
        return {"category": "VAL_RISCHI", "frequency": "variabile"}

    if "valutazione del rischio chimico" in t:
        return {"category": "VAL_RISCHI", "frequency": "triennale"}

    if "valutazione del rischio movimentazione manuale dei carichi" in t:
        return {"category": "VAL_RISCHI", "frequency": "quadriennale"}

    if "valutazione del rischio movimenti manuale di carichi" in t:
        return {"category": "VAL_RISCHI", "frequency": "quadriennale"}

    if "valutazione del rischio rumore" in t or "valutazione del richio rumore" in t:
        return {"category": "VAL_RISCHI", "frequency": "variabile"}

    if "valutazione dell esposizione dei lavoratori alle vibrazioni" in t \
       or "vibrazioni  civico" in t:
        return {"category": "VAL_RISCHI", "frequency": "variabile"}

    if "valutazione rischio campi elettr" in t:
        return {"category": "VAL_RISCHI", "frequency": "variabile"}

    if "rum1" in t or "valutazione di impatto acustico" in t:
        return {"category": "VAL_RISCHI", "frequency": "una_tantum"}

    # --- IMPIANTI / MACCHINARI / ELETTRICO / FOTOVOLTAICO / MESSE A TERRA / MANUTENZIONI ---
    if any(kw in t for kw in [
        "cabina mt bt",
        "impianto elettrico",
        "schema elettrico",
        "schemi elettrici",
        "impianto fotovoltaico",
        " messa a terra ",
        "messe a terra",
        "quadro bt cabina",
        "impianto di sollevamento paranco",
        "dichiarazione di conformit impianto cabina",
        "dichiarazione di conformit cabina elettrica",
        "dichiarazione di rispondenza impianto elettrico",
        "progetto impianto elettrico",
        "planimetria impianto elettrico",
        "manutenzionidalmec",
        "manutenzioni dalmec",
        "verifica gse impianto fotovoltaico",
    ]):
        if "manutenzionidalmec" in t or "manutenzioni dalmec" in t:
            return {"category": "IMPIANTI_MAC", "frequency": "annuale"}
        if "verifica impianto di messa a terra" in t or "verifica impianto di messa a terra inail" in t:
            return {"category": "IMPIANTI_MAC", "frequency": "biennale"}
        if "messe a terra" in t:
            return {"category": "IMPIANTI_MAC", "frequency": "una_tantum"}
        if "verifica gse impianto fotovoltaico" in t:
            return {"category": "IMPIANTI_MAC", "frequency": "annuale"}
        return {"category": "IMPIANTI_MAC", "frequency": "una_tantum"}

    if any(kw in t for kw in [
        "certificato ce",
        "garanzia",
        "manuale",
        "istruzioni assemblaggio",
        "conformita macchine",
        "conformita elba",
        "conformit elba",
        "abbattitore",
        "inkmaker",
        "montaclich",
        "rmac",
        "lava anilox",
        "targhe sacchettatrici",
        "comiflex",
        "mauale elba sav",
        "manuale elba sav",
    ]):
        return {"category": "IMPIANTI_MAC", "frequency": "una_tantum"}

    # --- INQUADRAMENTO AZIENDA (agibilità civici) ---
    if "agibilit" in t:
        return {"category": "INQ", "frequency": "variabile"}

    # --- LEGALE (videosorveglianza, ispettorato) ---
    if "videosorveglianza" in t or "ispettorato del lavoro" in t:
        return {"category": "LEG", "frequency": "una_tantum"}

    # --- QUALITA / DGF / flussi produttivi ---
    if "flusso produttivo" in t or "dgf1" in t or "dgf2" in t:
        return {"category": "QUAL", "frequency": "una_tantum"}

    # --- CONTRATTI FORNITURA (gas, elettrica) ---
    if "contratto fornitura gas metano" in t or "contratti fornitura energia elettrica" in t:
        return {"category": "INF_GEN", "frequency": "annuale"}

    # --- fallback: niente regola specifica ---
    return {"category": None, "frequency": None}


def _postprocess_suggestions(
    title: str,
    text: str,
    category: Optional[str],
    frequency: Optional[str],
    year: Optional[int],
) -> Dict[str, Any]:
    """
    Unisce AI + regole deterministiche.

    PRIORITÀ:
    - le regole (pattern forti tipo primo/pronto soccorso, MUD, polizza, DVR ecc.)
      VINCONO sempre sull'AI per category/frequency;
    - per l'anno ci fidiamo di più delle date trovate nel testo/titolo
      rispetto a un numero inventato dal modello.
    """
    norm_title = _normalize_text(title)
    norm_text = _normalize_text(text)
    fused = (norm_title + " " + norm_text).strip()

    # Heuristics da titolo+testo
    h = _heuristic_category_frequency_from_text(fused)
    h_cat = h.get("category")
    h_freq = h.get("frequency")

    # CATEGORY: normalizza AI, poi sovrascrivi se la regola ha un'idea
    cat = (category or "").strip().upper() or None
    if cat not in VALID_CATEGORIES:
        cat = None
    if h_cat:
        cat = h_cat  # le regole hanno priorità

    # FREQUENCY: normalizza AI, poi sovrascrivi se la regola ha un'idea
    freq = (frequency or "").strip().lower() or None
    if freq not in VALID_FREQUENCIES:
        freq = None
    if h_freq:
        freq = h_freq  # le regole hanno priorità

    # YEAR:
    extracted_year = _extract_year(title, text)
    if extracted_year is not None:
        year = extracted_year
    else:
        try:
            year = int(year) if year is not None else None
        except Exception:
            year = None

    return {
        "category": cat,
        "frequency": freq,
        "year": year,
    }


class AISuggestionService:
    """
    Service per suggerire i metadati di un documento aziendale
    (sicurezza, ambiente, legale, assicurazioni, qualità, nomine, ecc.).
    """

    def __init__(self) -> None:
        settings = get_settings()
        api_key: Optional[str] = getattr(settings, "GROQ_API_KEY", None)

        if not api_key:
            raise RuntimeError("GROQ_API_KEY non configurata nelle settings")

        self.client = Groq(api_key=api_key)

    def _call_llm(self, *, title: str, text: str) -> Dict[str, Any]:
        """
        Chiamata a Groq Llama 3.1 8B.
        Se qualcosa va storto, rilancia eccezione.
        """
        title = (title or "").strip()
        text = (text or "").strip()

        if len(text) > 8000:
            text = text[:8000]

        prompt = f"""
Sei un assistente per la classificazione di documenti aziendali italiani
(sicurezza sul lavoro, ambiente, nomine, assicurazioni, qualità, legale).

Devi analizzare TITOLO e TESTO del documento e restituire SOLO un JSON,
senza nessun testo extra, con questo schema esatto:

{{
  "category": "<UNO dei codici categoria>",
  "frequency": "<annuale|semestrale|biennale|triennale|quadriennale|quinquennale|una_tantum|variabile>",
  "year": 2024
}}

1) CATEGORY (ritorna il CODE, non la descrizione)

Scegli ESATTAMENTE UNO di questi codici, maiuscolo:

- INF_GEN     (informazioni generali, contratti fornitura, attestati generici)
- NOMINE      (nomine formali RLS, RSPP, addetti emergenza, datore di lavoro, ecc.)
- FORM_ADESTR (formazione e addestramento lavoratori, aggiornamenti, moduli formativi)
- VAL_RISCHI  (DVR, valutazioni di rischio specifiche, registro infortuni, impatto acustico, ecc.)
- MODULI      (moduli operativi/dpi/mulettisti/AAI/APS/da compilare)
- IMPIANTI_MAC (impianti elettrici, cabina MT/BT, fotovoltaico, macchine, manuali, CE, conformità, manutenzioni)
- EMERGENZA   (prove evacuazione, piani di emergenza)
- SORV_SAN    (sorveglianza sanitaria, protocolli medici, visite periodiche)
- INQ         (inquadramento azienda, agibilità civici)
- RIF         (rifiuti, MUD, gestione rifiuti)
- SAS         (serbatoi, suolo/sottosuolo/aree soggette a contaminazione)
- ASS         (assicurazioni, polizze)
- ATM         (AUA, emissioni in atmosfera, piano solventi)
- QUAL        (qualità, flussi produttivi, procedure di processo)
- LEG         (documenti legali, videosorveglianza, autorizzazioni ispettorato)
- VARIE       (tutto ciò che non rientra significativamente nelle categorie sopra)

Se nessuna categoria è davvero adatta, usa "VARIE".

2) FREQUENCY

Scegli una sola opzione tra:

- "annuale"
- "semestrale"
- "biennale"
- "triennale"
- "quadriennale"
- "quinquennale"
- "una_tantum"
- "variabile"

Linee guida (semplificate):

- Polizze, MUD, piano solventi, manutenzioni periodiche → di solito "annuale".
- Valutazioni rischio chimico → spesso "triennale".
- Valutazioni movimentazione manuale carichi → spesso "quadriennale".
- Valutazioni rumore, vibrazioni, campi elettrici → spesso "variabile".
- Nomine datore di lavoro, RLS, antincendio, mulettisti → spesso "quinquennale".
- Nomina addetti primo soccorso → spesso "triennale".
- Verifica impianto di messa a terra INAIL → spesso "biennale".
- Progetti, dichiarazioni di conformità, manuali, CE, agibilità, autorizzazioni videosorveglianza, AUA di adozione → "una_tantum".
- Se non è chiaro, scegli comunque una delle opzioni, meglio prudente.

3) YEAR

- Cerca anni (2015, 2020, 2023, 2025, ecc.) nel titolo e nel testo.
- Scegli l'anno principale del documento, di solito il più recente legato al contenuto.
- Se non trovi nessun anno, puoi usare l'anno corrente come stima.

Restituisci SOLO il JSON, senza commenti e senza testo extra.

TITOLO:
\"\"\"{title}\"\"\"


TESTO:
\"\"\"{text}\"\"\""""

        resp = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256,
        )

        content = resp.choices[0].message.content

        if isinstance(content, list):
            content = "".join(
                (part.get("text", "") if isinstance(part, dict) else str(part))
                for part in content
            )

        raw = (content or "").strip()
        data = json.loads(raw)
        return data

    def suggest_doc_metadata(self, *, title: str, text: str) -> Dict[str, Any]:
        """
        Ritorna sempre un dict con chiavi:
        - category: codice categoria (es. 'VAL_RISCHI', 'IMPIANTI_MAC', 'ASS', ecc.) oppure None
        - frequency: 'annuale' | 'semestrale' | 'biennale' | 'triennale' |
                     'quadriennale' | 'quinquennale' | 'una_tantum' | 'variabile' oppure None
        - year: int oppure None
        """
        try:
            data = self._call_llm(title=title, text=text)
        except Exception as e:
            logger.warning("AI suggest_doc_metadata failed (LLM): %s", e, exc_info=True)
            norm_title = _normalize_text(title)
            norm_text = _normalize_text(text)
            fused = (norm_title + " " + norm_text).strip()
            h = _heuristic_category_frequency_from_text(fused)
            year = _extract_year(title, text)
            return {
                "category": h.get("category"),
                "frequency": h.get("frequency"),
                "year": year,
            }

        cat = (data.get("category") or "").strip().upper() or None
        freq = (data.get("frequency") or "").strip().lower() or None
        year = data.get("year")

        if cat not in VALID_CATEGORIES:
            cat = None
        if freq not in VALID_FREQUENCIES:
            freq = None
        try:
            year = int(year) if year is not None else None
        except Exception:
            year = None

        return _postprocess_suggestions(
            title=title,
            text=text,
            category=cat,
            frequency=freq,
            year=year,
        )
