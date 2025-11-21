from __future__ import annotations

import re
from pathlib import Path
from datetime import date, datetime

from app.settings import get_settings
from app.db.db import DbManager, MySQLDb, QueryType


def _safe_chunk(s: str) -> str:
    """Sanitizza CF / codici per usarli come nome cartella."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", (s or "").strip())


def _to_date(val):
    """Accetta date MySQL (date, datetime, str o None) e restituisce date o None."""
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            # formato tipico 'YYYY-MM-DD'
            return datetime.fromisoformat(val).date()
        except Exception:
            return None
    return None


def main():
    settings = get_settings()

    # Base path: es. C:/PlaxData/CertificazioniDipendenti
    base_root = Path(settings.CERTS_BASE_DIR)
    cert_root = base_root / "Certificazioni"

    print(f"[INFO] CERTS_BASE_DIR: {base_root}")
    print(f"[INFO] Uso root certificazioni: {cert_root}")

    if not cert_root.exists():
        print(f"[ERRORE] La cartella {cert_root} non esiste. Correggi il percorso nel codice o nelle settings.")
        return

    with DbManager(MySQLDb()) as db:
        # prendo TUTTE le certificazioni con dati necessari per ricostruire il path
        sql = """
            SELECT
                oc.id,
                oc.operator_id,
                oc.cert_type_id,
                oc.issue_date,
                oc.expiry_date,
                oc.file_path,
                o.fiscal_code,
                t.code AS cert_code
            FROM operator_certifications oc
            JOIN operators o ON o.id = oc.operator_id
            JOIN operator_cert_types t ON t.id = oc.cert_type_id
        """
        rows = db.execute_query(sql, query_type=QueryType.GET)

    print(f"[INFO] Trovate {len(rows)} certificazioni da analizzare.")

    updates = []
    missing = []

    for r in rows:
        cert_id = int(r["id"])
        op_id = int(r["operator_id"])
        cert_type_id = int(r["cert_type_id"])
        fiscal_code = (r.get("fiscal_code") or "").strip().upper()
        cert_code = (r.get("cert_code") or "").strip().upper() or f"CERT_{cert_type_id}"

        issue = _to_date(r.get("issue_date"))
        expiry = _to_date(r.get("expiry_date"))

        # CF fallback se assente
        if not fiscal_code:
            cf_label = f"OP_{op_id}"
        else:
            cf_label = fiscal_code

        cf_folder = _safe_chunk(cf_label)
        cert_code_chunk = _safe_chunk(cert_code)

        # stessa logica usata dal service: scadenza se c'è, altrimenti rilascio
        chosen_dt = expiry or issue
        dstr = chosen_dt.strftime("%Y%m%d") if chosen_dt else None

        dir_path = cert_root / cf_folder
        if not dir_path.exists():
            missing.append((cert_id, "no_cf_dir", str(dir_path)))
            continue

        candidate = None

        # se abbiamo una data, cerchiamo CODICE_YYYYMMDD* (gestione __1, __2)
        if dstr:
            pattern = f"{cert_code_chunk}_{dstr}*"
            matches = list(dir_path.glob(pattern))
            if matches:
                # se ce ne sono più, prendo quello "più vecchio" alfabeticamente
                candidate = sorted(matches)[0]

        # se non abbiamo trovato nulla ma esistono file con quel codice, uso il primo
        if candidate is None:
            pattern = f"{cert_code_chunk}_*"
            matches = list(dir_path.glob(pattern))
            if matches:
                candidate = sorted(matches)[0]

        if candidate is None:
            # nessun file trovato per questa certificazione
            descr = f"{cert_code_chunk}_{dstr or '*'} in {dir_path}"
            missing.append((cert_id, "no_file", descr))
            continue

        new_path = str(candidate)

        # se è diverso da quello memorizzato, lo aggiungo alla lista di update
        old_path = r.get("file_path")
        if old_path != new_path:
            updates.append((cert_id, old_path, new_path))

    # riepilogo
    print(f"[INFO] Da aggiornare: {len(updates)} record.")
    print(f"[INFO] Mancanti/non trovati: {len(missing)} record.")

    # eseguo UPDATE
    if updates:
        with DbManager(MySQLDb()) as db:
            for cert_id, old_path, new_path in updates:
                db.execute_query(
                    "UPDATE operator_certifications SET file_path = %s WHERE id = %s",
                    [new_path, int(cert_id)],
                    query_type=QueryType.UPDATE,
                )

    # log finale
    if updates:
        print("=== AGGIORNAMENTI ESEGUITI ===")
        for cert_id, old_path, new_path in updates:
            print(f"  [ID {cert_id}]")
            print(f"    vecchio: {old_path}")
            print(f"    nuovo:   {new_path}")

    if missing:
        print("=== NON TROVATI ===")
        for cert_id, reason, descr in missing:
            print(f"  [ID {cert_id}] {reason} -> {descr}")

    print("[DONE] Sistemazione percorsi completata.")


if __name__ == "__main__":
    main()
