"""
Script UNA TANTUM per migrare gli allegati delle certificazioni
nella nuova struttura:

    <CERTS_BASE_DIR>/Certificazioni/<TIPO>/<CF>/<TIPO>_YYYYMMDD.ext

ATTENZIONE:
- Fai PRIMA un backup della cartella CERTS_BASE_DIR.
- Esegui questo script solo una volta (o idempotente ma non abusarne).
"""

from pathlib import Path
from datetime import date
import re
import shutil

from app.settings import get_settings
from app.db.db import DbManager, MySQLDb, QueryType


def safe_chunk(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", (s or "").strip())


def pick_date_for_filename(issue, expiry) -> date:
    """
    Usa expiry se presente, altrimenti issue, altrimenti oggi.
    issue/expiry arrivano come date o None dal driver MySQL.
    """
    if expiry:
        return expiry
    if issue:
        return issue
    return date.today()


def base_root() -> Path:
    settings = get_settings()
    base = settings.CERTS_BASE_DIR
    return Path(base) / "Certificazioni"


def migrate():
    base = base_root()
    base.mkdir(parents=True, exist_ok=True)

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
        WHERE oc.file_path IS NOT NULL
    """

    with DbManager(MySQLDb()) as db:
        rows = db.execute_query(sql, query_type=QueryType.GET)

        print(f"Trovate {len(rows)} certificazioni con file_path non nullo")

        for r in rows:
            cert_id = r["id"]
            op_id = r["operator_id"]
            issue = r["issue_date"]   # tipo date o None
            expiry = r["expiry_date"] # tipo date o None
            old_path = r["file_path"]
            cf = (r.get("fiscal_code") or "").strip().upper()
            cert_code = (r.get("cert_code") or "").strip().upper() or f"CERT_{r['cert_type_id']}"

            if not old_path:
                print(f"[SKIP] id={cert_id}: file_path vuoto")
                continue

            old = Path(old_path)
            if not old.exists():
                print(f"[WARN] id={cert_id}: file non trovato su disco: {old}")
                continue

            cf_chunk = safe_chunk(cf) if cf else f"OP_{op_id}"
            cert_chunk = safe_chunk(cert_code)

            chosen_dt = pick_date_for_filename(issue, expiry)
            dstr = f"{chosen_dt:%Y%m%d}"

            ext = ""
            name = old.name
            if "." in name:
                ext = "." + name.split(".")[-1].lower()

            filename = f"{cert_chunk}_{dstr}{ext}"
            dest_dir = base / cert_chunk / cf_chunk
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / filename

            # evita collisioni: aggiungi __1, __2, ...
            candidate = dest
            i = 1
            while candidate.exists():
                candidate = dest.with_stem(f"{dest.stem}__{i}")
                i += 1

            print(f"[MOVE] id={cert_id}: {old} -> {candidate}")
            shutil.move(str(old), str(candidate))

            # aggiorna DB con il nuovo path
            upd_sql = "UPDATE operator_certifications SET file_path = %s WHERE id = %s"
            db.execute_query(upd_sql, [str(candidate), int(cert_id)], query_type=QueryType.UPDATE)


if __name__ == "__main__":
    migrate()
    print("Migrazione completata.")
