from datetime import datetime
from typing import List, Optional, Dict, Any
from app.repo.JobRepository import JobRepository
from app.repo.ClientRepository import ClientRepository
from app.repo.ArticleRepository import ArticleRepository
from app.repo.LotRepository import LotRepository
from app.repo.MachineRepository import MachineRepository
from app.repo.OperatorRepository import OperatorRepository


class JobService:
    def __init__(self):
        self.job_repo = JobRepository()
        self.client_repo = ClientRepository()
        self.article_repo = ArticleRepository()
        self.lot_repo = LotRepository()
        self.machine_repo = MachineRepository()
        self.operator_repo = OperatorRepository()

    # -------------------- util interne --------------------
    def _determine_shift(self, start_time: str) -> str:
        """
        Calcola il turno a partire dall'ora di inizio.
        Accetta 'HH:MM', 'HH:MM:SS', 'YYYY-MM-DD HH:MM[:SS]', 'YYYY-MM-DDTHH:MM[:SS]'.
        """
        if not start_time:
            return ""
        s = start_time.strip()

        # parsing robusto per i formati più comuni
        fmts = ["%H:%M", "%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"]
        hour = None
        for f in fmts:
            try:
                hour = datetime.strptime(s, f).hour
                break
            except ValueError:
                continue
        if hour is None:
            # ultimo tentativo: solo ore (es. '6' o '06')
            try:
                hour = int(s.split(":")[0])
            except Exception:
                return ""

        if 6 <= hour < 14:
            return "MATTINA"
        elif 14 <= hour < 21:
            return "POMERIGGIO"
        else:
            return "SERA"

    def _to_opt_number(self, v, cast=float):
        """Converte stringa vuota in None; altrimenti cast (int/float)."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return v
        s = str(v).strip()
        if s == "":
            return None
        try:
            return cast(s)
        except Exception:
            return None

    # -------------------------------------------------------------------------
    # JOB CREATION
    # -------------------------------------------------------------------------
    def create_job(
        self,
        job_date: str,
        process_type: str,
        machine_id: int,
        lot_code: str,
        client_name: str,
        article_code: Optional[str],
        article_description: Optional[str],
        start_time: str,
        end_time: str,
        meters_produced: Optional[int],
        scrap_meters: Optional[int],
        scrap_kg: Optional[float],
        setup_meters: Optional[int],
        shift_label: Optional[str],
        notes: Optional[str],
        operator_ids: List[int],
        quality_checks: Optional[List[Dict[str, Any]]] = None,
        materials: Optional[List[Dict[str, Any]]] = None,
        consumables: Optional[List[Dict[str, Any]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        properties: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Crea una scheda lavoro completa:
        - cliente, articolo, lotto (se non esistono)
        - job principale
        - operatori, controlli, materiali, consumabili, eventi, proprietà opzionali
        """
        # normalizza opzionali (supporta stringhe vuote dal form)
        meters_produced = self._to_opt_number(meters_produced, int)
        scrap_meters    = self._to_opt_number(scrap_meters, int)
        scrap_kg        = self._to_opt_number(scrap_kg, float)
        setup_meters    = self._to_opt_number(setup_meters, int)

        # turno automatico se non valorizzato dal frontend
        if not shift_label or str(shift_label).strip() == "":
            shift_label = self._determine_shift(start_time)

        # Normalizza cliente/articolo/lotto
        client_id = self.client_repo.get_or_create(client_name)
        article_id = self.article_repo.get_or_create(article_code, article_description, client_id)
        lot_id = self.lot_repo.get_or_create(lot_code, client_id, article_id)

        # Crea il job principale
        job_id = self.job_repo.create_job({
            "job_date": job_date,
            "machine_id": machine_id,
            "process_type": process_type,
            "lot_id": lot_id,
            "start_time": start_time,
            "end_time": end_time,
            "meters_produced": meters_produced,
            "scrap_meters": scrap_meters,
            "scrap_kg": scrap_kg,
            "setup_meters": setup_meters,
            "notes": notes,
            "shift_label": shift_label,
        })

        # Collega operatori
        for op_id in operator_ids or []:
            self.job_repo.attach_operator(job_id, op_id)

        # Controlli qualità
        if quality_checks:
            for qc in quality_checks:
                self.job_repo.add_quality_check(
                    job_id,
                    qc.get("check_type_code"),
                    qc.get("result"),
                    qc.get("value_text"),
                )

        # Materiali (es. adesivo)
        if materials:
            for m in materials:
                self.job_repo.add_material(
                    job_id,
                    m.get("material_type"),
                    m.get("material_name"),
                    m.get("lot_number"),
                    self._to_opt_number(m.get("quantity"), float),
                    m.get("unit"),
                    self._to_opt_number(m.get("setpoint_value"), float),
                )

        # Consumabili (es. lame)
        if consumables:
            for c in consumables:
                self.job_repo.add_consumable(
                    job_id,
                    c.get("consumable_type"),
                    self._to_opt_number(c.get("quantity"), float),
                    c.get("unit"),
                    c.get("notes"),
                )

        # Eventi (fermi, scarti)
        if events:
            for e in events:
                self.job_repo.add_event(
                    job_id,
                    e.get("event_type"),
                    e.get("reason"),
                    self._to_opt_number(e.get("minutes"), int),
                    self._to_opt_number(e.get("quantity_m"), int),
                    self._to_opt_number(e.get("quantity_kg"), float),
                )

        # Proprietà aggiuntive (EAV)
        if properties:
            for p in properties:
                self.job_repo.set_property(job_id, p.get("prop_key"), p.get("prop_value"))

        return job_id

    # -------------------------------------------------------------------------
    # JOB READ / LIST / META come già li hai ...
    def get_job_detail(self, job_id: int) -> dict:
        job = self.job_repo.get_job(job_id)
        if not job:
            return {}
        job["operators"] = self.job_repo.list_job_operators(job_id)
        job["quality_checks"] = self.job_repo.list_quality_checks(job_id)
        job["materials"] = self.job_repo.list_materials(job_id)
        job["consumables"] = self.job_repo.list_consumables(job_id)
        job["events"] = self.job_repo.list_events(job_id)
        job["properties"] = self.job_repo.list_properties(job_id)
        return job

    def list_jobs_by_machine_and_date(self, job_date: str, machine_id: int):
        return self.job_repo.list_jobs_by_day_machine(job_date, machine_id)

    def list_all_machines(self):
        return self.machine_repo.get_all()

    def list_all_operators(self):
        return self.operator_repo.list()

    def list_operators(self, department_id: Optional[int] = None, q: Optional[str] = None):
        return self.operator_repo.list(department_id=department_id, q=q)