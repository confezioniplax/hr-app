from __future__ import annotations
from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import date, datetime

from fastapi.encoders import jsonable_encoder

from app.repo.HRRepository import HRRepository


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
    ) -> int:
        issue = self._parse_date(issue_date)
        expiry = self._parse_date(expiry_date)
        return int(
            self.repo.upsert_certification(
                id=id,
                operator_id=operator_id,
                cert_type_id=cert_type_id,
                status=status,
                issue_date=issue,
                expiry_date=expiry,
                notes=(notes or "").strip() or None,
            )
        )

    def delete_certification(self, cert_id: int) -> None:
        self.repo.delete_certification(cert_id)

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

    # -------- helpers --------
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
        # normalizza formati: prima rimuove i separatori delle migliaia, poi converte la virgola in punto
        if "," in txt and "." in txt:
            # caso tipico italia con punti come migliaia e virgola come decimali
            txt = txt.replace(".", "").replace(",", ".")
        elif "," in txt and "." not in txt:
            # solo virgola come decimali
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
