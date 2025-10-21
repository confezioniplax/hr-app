import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Depends, Form
from fastapi.responses import JSONResponse

from app.services.JobService import JobService
from app.repo.OperatorRepository import OperatorRepository
from app.services.AuthenticationService import AuthenticationService

api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.post("/jobs/create")
async def create_job(
    request: Request,
    job_date: str = Form(...),
    process_type: str = Form(...),
    machine_id: int = Form(...),
    lot_code: str = Form(...),
    client_name: str = Form(...),
    article_code: str = Form(""),
    article_description: str = Form(""),

    start_time: str = Form(""),
    end_time: str = Form(""),

    # ⚠️ allineati ai nomi dei form HTML
    meters_produced: str = Form(""),
    scrap_m: str = Form(""),           # era scrap_meters nei tuoi esempi
    scrap_kg: str = Form(""),
    mt_startup: str = Form(""),        # era setup_meters nei tuoi esempi

    shift_label: str = Form(""),
    notes: str = Form(""),

    # array JSON dal form (stringhe)
    operator_ids: str = Form("[]"),
    quality_checks: str = Form("[]"),
    materials: str = Form("[]"),
    consumables: str = Form("[]"),
    events: str = Form("[]"),
    properties: str = Form("[]"),

    service: JobService = Depends(JobService),
):
    def _loads_or_default(s: str, default):
        try:
            return json.loads(s) if s and s.strip() else default
        except Exception:
            return default

    operator_list = _loads_or_default(operator_ids, [])
    qc_list       = _loads_or_default(quality_checks, [])
    mat_list      = _loads_or_default(materials, [])
    cons_list     = _loads_or_default(consumables, [])
    evt_list      = _loads_or_default(events, [])
    prop_list     = _loads_or_default(properties, [])

    try:
        job_id = service.create_job(
            job_date=job_date,
            process_type=process_type,
            machine_id=machine_id,
            lot_code=lot_code,
            client_name=client_name,
            article_code=article_code or None,
            article_description=article_description or None,
            start_time=start_time or "",
            end_time=end_time or "",

            # mapping coerente con JobService
            meters_produced=meters_produced,
            scrap_meters=scrap_m,      # ← arrivava vuoto con scrap_meters
            scrap_kg=scrap_kg,
            setup_meters=mt_startup,   # ← arrivava vuoto con setup_meters

            shift_label=shift_label,
            notes=notes,

            operator_ids=operator_list,
            quality_checks=qc_list,
            materials=mat_list,
            consumables=cons_list,
            events=evt_list,
            properties=prop_list,
        )
        return JSONResponse(status_code=200, content={"message": "Job created successfully", "job_id": job_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@api_router.get("/jobs/detail")
async def get_job_detail(
    job_id: int = Query(...),
    service: JobService = Depends(JobService)
):
    """Dettaglio completo di una scheda lavoro."""
    try:
        job = service.get_job_detail(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JSONResponse(status_code=200, content=job)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading job: {str(e)}")


@api_router.get("/jobs/list")
async def list_jobs_by_machine(
    job_date: str = Query(...),
    machine_id: int = Query(...),
    service: JobService = Depends(JobService)
):
    """Elenco job giornalieri per macchina."""
    try:
        data = service.list_jobs_by_machine_and_date(job_date, machine_id)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing jobs: {str(e)}")


# ===== META =====

@api_router.get("/jobs/meta/machines")
async def list_machines(
    service: JobService = Depends(JobService),
    department_id: Optional[int] = Query(default=None)
):
    """
    Restituisce elenco macchine attive.
    Se presente ?department_id= filtra (richiede che i record abbiano 'department_id').
    """
    try:
        data = service.list_all_machines()
        if department_id is not None:
            data = [m for m in data if (("department_id" in m) and (m["department_id"] == department_id))]
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing machines: {str(e)}")

@api_router.get("/jobs/meta/operators")
async def list_operators(
    service: JobService = Depends(JobService),
    department_id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None)
):
    """
    Elenco operatori attivi.
    - ?department_id= filtra via JOIN su operator_departments
    - ?q= ricerca semplice su nome/cognome
    """
    try:
        data = service.list_operators(department_id=department_id, q=q)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing operators: {str(e)}")

# ===== AUTH SEED =====

@api_router.post("/bootstrap_auth_seed")
async def bootstrap_auth_seed():
    """
    Crea/aggiorna utente:
      email:    riccardo@plaxpackaging.it
      password: plax
      role:     HR
    """
    repo = OperatorRepository()
    email = "riccardo@plaxpackaging.it"
    pw_hash = AuthenticationService.hash_password("plax")
    user = repo.get_by_email(email)
    if user:
        repo.update_password_and_role(user["id"], pw_hash, "HR")
        return JSONResponse(status_code=200, content={"message": f"User '{email}' updated"})
    else:
        repo.create_with_auth("Riccardo", "Leonelli", email, pw_hash, "HR")
        return JSONResponse(status_code=201, content={"message": f"User '{email}' created"})
