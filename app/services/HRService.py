from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path
import re

from fastapi.encoders import jsonable_encoder
from app.services.email_sender import EmailSender
from app.repo.HRRepository import HRRepository
from app.settings import get_settings


class HRService:
    def __init__(self):
        self.repo = HRRepository()

    # -------- META --------
    def list_departments(self) -> List[Dict[str, Any]]:
        return self._encode(self.repo.list_departments())

    def list_cert_types(self) -> List[Dict[str, Any]]:
        return self._encode(self.repo.list_cert_types())

    def list_operators_light(self, active: Optional[int] = 1) -> List[Dict[str, Any]]:
        return self._encode(self.repo.list_operators_light(active=active))

    # -------- ANAGRAFICA --------
    def list_operator_core(self, q=None, department_id=None, active=None) -> List[Dict[str, Any]]:
        return self._encode(self.repo.list_operator_core(q=q, department_id=department_id, active=active))

    def get_operator(self, op_id: int) -> Optional[Dict[str, Any]]:
        op = self.repo.get_operator(op_id)
        return self._encode(op) if op else None

    def create_operator(
        self,
        *,
        first_name: str,
        last_name: str,
        fiscal_code: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        birth_date: Optional[str] = None,
        citizenship: Optional[str] = None,
        education_level: Optional[str] = None,
        hire_date: Optional[str] = None,
        contract_type: Optional[str] = None,
        contract_expiry: Optional[str] = None,
        level: Optional[str] = None,
        ral: Optional[str] = None,
        departments: Optional[str] = None,
        active: Optional[int] = 1,
    ) -> int:
        bd = self._parse_date(birth_date)
        hd = self._parse_date(hire_date)
        ce = self._parse_date(contract_expiry)
        rl = self._parse_decimal(ral)  # accetta "35500.00" o "35.500,00"
        self._validate_non_negative(rl, field="ral")

        act = None if active is None else (1 if int(active) == 1 else 0)

        return int(
            self.repo.create_operator(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                fiscal_code=(fiscal_code or "").strip() or None,
                phone=(phone or "").strip() or None,
                email=(email or "").strip() or None,
                address=(address or "").strip() or None,
                birth_date=bd,
                citizenship=(citizenship or "").strip() or None,
                education_level=(education_level or "").strip() or None,
                hire_date=hd,
                contract_type=(contract_type or "").strip() or None,
                contract_expiry=ce,
                level=(level or "").strip() or None,
                ral=rl,
                departments=(departments or "").strip() or None,
                active=act,
            )
        )

    def update_operator(
        self,
        *,
        id: int,
        first_name: str,
        last_name: str,
        fiscal_code: Optional[str] = None,
        phone: Optional[str] = None,
        birth_date: Optional[str] = None,
        citizenship: Optional[str] = None,
        education_level: Optional[str] = None,
        hire_date: Optional[str] = None,
        contract_type: Optional[str] = None,
        contract_expiry: Optional[str] = None,
        level: Optional[str] = None,
        ral: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        departments: Optional[str] = None,
        active: Optional[int] = 1,
    ) -> None:
        bd = self._parse_date(birth_date)
        hd = self._parse_date(hire_date)
        ce = self._parse_date(contract_expiry)
        rl = self._parse_decimal(ral)
        self._validate_non_negative(rl, field="ral")

        act = None if active is None else (1 if int(active) == 1 else 0)

        self.repo.update_operator(
            id=id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            fiscal_code=(fiscal_code or "").strip() or None,
            phone=(phone or "").strip() or None,
            birth_date=bd,
            citizenship=(citizenship or "").strip() or None,
            education_level=(education_level or "").strip() or None,
            hire_date=hd,
            contract_type=(contract_type or "").strip() or None,
            contract_expiry=ce,
            level=(level or "").strip() or None,
            ral=rl,
            email=(email or "").strip() or None,
            address=(address or "").strip() or None,
            departments=(departments or "").strip() or None,
            active=act,
        )

    # -------- CERTIFICAZIONI --------
    def list_cert_status(
        self,
        department_id: Optional[int] = None,
        cert_type_id: Optional[int] = None,
        status_calc: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        rows = self.repo.list_cert_status(
            department_id=department_id,
            cert_type_id=cert_type_id,
            status_calc=status_calc,
            operator_id=operator_id,
        )
        return self._encode(rows)

    def upsert_certification(
        self,
        *,
        id: Optional[int],
        operator_id: int,
        cert_type_id: int,
        status: str,
        issue_date: Optional[str],
        expiry_date: Optional[str],
        notes: Optional[str],
        # 👇 nuovo: contenuto e nome originale del file (se presente)
        file_bytes: Optional[bytes] = None,
        original_filename: Optional[str] = None,
    ) -> int:
        """
        Salva/aggiorna la certificazione.
        Se `file_bytes` e `original_filename` sono presenti, salva l'allegato su disco in:
            <BASE>/Certificazioni/<CF>/<TIPO>_<DATA>.<ext>
        e passa `file_path` al repository.
        """
        issue = self._parse_date(issue_date)
        expiry = self._parse_date(expiry_date)

        file_path: Optional[str] = None
        if file_bytes and original_filename:
            file_path = self._save_cert_attachment(
                operator_id=operator_id,
                cert_type_id=cert_type_id,
                issue_date=issue,
                expiry_date=expiry,
                original_filename=original_filename,
                content=file_bytes,
            )

        return int(
            self.repo.upsert_certification(
                id=id,
                operator_id=operator_id,
                cert_type_id=cert_type_id,
                status=status,
                issue_date=issue,
                expiry_date=expiry,
                notes=(notes or "").strip() or None,
                file_path=file_path,
            )
        )

    def delete_certification(self, cert_id: int) -> None:
        self.repo.delete_certification(cert_id)

    def get_certification(self, cert_id: int) -> Optional[Dict[str, Any]]:
        """Serve per il download dell'allegato."""
        row = self.repo.get_certification(cert_id)
        return self._encode(row) if row else None

    # -------- KPI --------
    def get_kpi(self, department_id=None, cert_type_id=None, status_calc=None) -> Dict[str, Any]:
        tot_attivi = self.repo.count_active_operators(department_id)
        rows = self.repo.list_cert_status(
            department_id=department_id, cert_type_id=cert_type_id, status_calc=status_calc
        )
        if not rows:
            return {
                "tot_operatori_attivi": int(tot_attivi or 0),
                "pct_ok_avg": 0,
                "n_in_scadenza": 0,
                "n_scadute": 0,
            }
        ok = sum(1 for r in rows if r.get("status_calc") == "OK")
        scad = sum(1 for r in rows if r.get("status_calc") == "SCADUTA")
        in_scad = sum(1 for r in rows if (r.get("status_calc") or "").startswith("IN_SCADENZA"))
        pct_ok = round((ok / max(len(rows), 1)) * 100) if rows else 0
        return {
            "tot_operatori_attivi": int(tot_attivi or 0),
            "pct_ok_avg": int(pct_ok or 0),
            "n_in_scadenza": int(in_scad or 0),
            "n_scadute": int(scad or 0),
        }

    # =======================
    #  Helpers & File Saving
    # =======================
    def _encode(self, obj: Any) -> Any:
        data = jsonable_encoder(obj)
        if isinstance(data, list):
            for r in data:
                for k, v in list(r.items()):
                    if isinstance(v, Decimal):
                        r[k] = float(v)
        elif isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, Decimal):
                    data[k] = float(v)
        return data

    @staticmethod
    def _parse_date(s: Optional[str]) -> Optional[date]:
        if not s:
            return None
        s = s.strip()
        try:
            # formati "YYYY-MM-DD"
            y, m, d = s.split("-")
            return date(int(y), int(m), int(d))
        except Exception:
            try:
                dt = datetime.fromisoformat(s)
                return dt.date()
            except Exception:
                raise ValueError(f"Formato data non valido: {s}")

    @staticmethod
    def _parse_decimal(s: Optional[str]) -> Optional[float]:
        """
        Converte stringhe italiane ('35.500,00') o inglesi ('35500.00') in float.
        Restituisce None se s è vuoto.
        """
        if s is None:
            return None
        txt = str(s).strip()
        if txt == "":
            return None
        if "," in txt and "." in txt:
            txt = txt.replace(".", "").replace(",", ".")
        elif "," in txt and "." not in txt:
            txt = txt.replace(",", ".")
        try:
            val = float(txt)
        except ValueError:
            raise ValueError(f"Formato numerico non valido per RAL: {s}")
        return val

    @staticmethod
    def _validate_non_negative(val: Optional[float], *, field: str) -> None:
        if val is not None and val < 0:
            raise ValueError(f"{field} non può essere negativo")

    # ---------- File path logic ----------
    def _safe_chunk(self, s: str) -> str:
        """Sanifica una parte di percorso/nome file."""
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", (s or "").strip())

    def _pick_date_for_filename(self, issue: Optional[date], expiry: Optional[date]) -> date:
        """Usa scadenza se presente, altrimenti rilascio, altrimenti oggi."""
        if isinstance(expiry, date):
            return expiry
        if isinstance(issue, date):
            return issue
        return date.today()

    def _get_operator_fiscal_code(self, operator_id: int) -> str:
        op = self.repo.get_operator(operator_id) or {}
        cf = (op.get("fiscal_code") or "").strip()
        return cf.upper() if cf else f"OP_{operator_id}"

    def _get_cert_type_code(self, cert_type_id: int) -> str:
        # non do per scontato un getter dedicato; filtro dalla lista
        types = self.repo.list_cert_types() or []
        for t in types:
            if int(t.get("id", 0)) == int(cert_type_id):
                code = (t.get("code") or "").strip()
                return code.upper() if code else f"CERT_{cert_type_id}"
        return f"CERT_{cert_type_id}"

    def _build_attachment_dest(
        self,
        *,
        operator_id: int,
        cert_type_id: int,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        original_filename: str,
    ) -> Path:
        """
        Costruisce il path finale:
            <BASE>/Certificazioni/<CF>/<TIPO>_<YYYYMMDD>.<ext>
        """
        base_root = Path(get_settings().CERTS_BASE_DIR)  # configurabile: es. "C:/Certificazioni" o "/data"
        root = base_root / "Certificazioni"

        cf = self._safe_chunk(self._get_operator_fiscal_code(operator_id))
        cert_code = self._safe_chunk(self._get_cert_type_code(cert_type_id))

        chosen_dt = self._pick_date_for_filename(issue_date, expiry_date)
        dstr = f"{chosen_dt:%Y%m%d}"

        # estensione originale (se presente)
        ext = ""
        name = (original_filename or "").strip()
        if "." in name:
            ext = "." + name.split(".")[-1].lower()

        filename = f"{cert_code}_{dstr}{ext}"
        dest_dir = root / cf
        dest_dir.mkdir(parents=True, exist_ok=True)
        return dest_dir / filename

    def _save_cert_attachment(
        self,
        *,
        operator_id: int,
        cert_type_id: int,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        original_filename: str,
        content: bytes,
    ) -> str:
        """
        Salva fisicamente l'allegato e ritorna il percorso stringa.
        """
        dest = self._build_attachment_dest(
            operator_id=operator_id,
            cert_type_id=cert_type_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            original_filename=original_filename,
        )
        # se esiste già, aggiungo un suffisso numerico
        candidate = dest
        i = 1
        while candidate.exists():
            candidate = dest.with_stem(f"{dest.stem}__{i}")
            i += 1

        candidate.write_bytes(content)
        return str(candidate)

    # -------- NOTIFICHE EMAIL SCADENZE --------
    def send_expiring_certs_email_if_needed(
        self,
        *,
        recipient_email: str,
        days: int = 30,
        department_id: int | None = None,
        frequency_days: int = 7  # ✅ invia al massimo ogni 7 giorni
    ) -> dict:
        rows = self.repo.list_expiring_certs(days=days, department_id=department_id)

        if not rows:
            return {"sent": False, "n_rows": 0, "reason": "no-data"}

        today = date.today()
        event_code = "EXPIRY_REMINDER_LOGIN"

        if self.repo.notification_sent_in_window(
            event_code=event_code, sent_to=recipient_email, days_window=frequency_days
        ):
            return {"sent": False, "n_rows": len(rows), "reason": f"throttled-{frequency_days}d-window"}

        if self.repo.notification_already_sent(
            event_code=event_code, ref_date=today, sent_to=recipient_email, payload=rows
        ):
            return {"sent": False, "n_rows": len(rows), "reason": "already-sent-today"}

        def esc(x): 
            return (str(x) if x is not None else "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

        header = f"""
            <h3>Certificazioni SCADUTE e in scadenza entro {days} giorni</h3>
            <p>Data: {today.strftime("%Y-%m-%d")}</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
              <thead>
                <tr>
                  <th>Operatore</th>
                  <th>Reparti</th>
                  <th>Certificazione</th>
                  <th>Scadenza</th>
                  <th>Giorni residui</th>
                  <th>Stato</th>
                </tr>
              </thead>
              <tbody>
        """
        body_rows = []
        for r in rows:
            name = esc(r.get('operator_name'))
            deps = esc(r.get('departments') or '')
            cert = esc(r.get('cert_code'))
            exp  = esc(r.get('expiry_date'))
            try:
                dl = int(r.get('days_left'))
            except Exception:
                dl = None

            if dl is None:
                stato = "N/D"
                style_row = ""
                dl_text = ""
            elif dl < 0:
                stato = f"SCADUTA da {abs(dl)} gg"
                style_row = " style='background:#ffe6e6;'"
                dl_text = str(dl)
            elif dl == 0:
                stato = "OGGI"
                style_row = " style='background:#fff5cc;'"
                dl_text = "0"
            else:
                stato = f"tra {dl} gg"
                style_row = ""
                dl_text = str(dl)

            body_rows.append(
                f"<tr{style_row}>"
                f"<td>{name}</td>"
                f"<td>{deps}</td>"
                f"<td>{cert}</td>"
                f"<td>{exp}</td>"
                f"<td style='text-align:right'>{dl_text}</td>"
                f"<td>{stato}</td>"
                "</tr>"
            )
        footer = "</tbody></table>"
        html = header + "\n".join(body_rows) + footer

        EmailSender().send_html(
            to=[recipient_email],
            subject=f"[PLAX] Report settimanale — Certificazioni SCADUTE e in scadenza ≤ {days} gg",
            html=html
        )

        self.repo.notification_log_insert(
            event_code=event_code, ref_date=today, sent_to=recipient_email, payload=rows
        )
        return {"sent": True, "n_rows": len(rows), "reason": "ok"}
