from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import TokenData, get_current_employee, get_current_manager
from app.services.JobService import JobService
import json

view_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Mappa reparti
DEPT_STAMPA = 1
DEPT_TAGLIO = 2
DEPT_ACCO   = 3

def _layout_for(user: TokenData) -> str:
    # Manager (HR/CEO) usa layout_manager, altrimenti layout_employee
    return "layout_manager.html" if user.role in ("HR", "CEO") else "layout_employee.html"

def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _machines_for_department(service: JobService, dept_id: int):
    """
    Recupera tutte le macchine e filtra per department_id se presente.
    Così non obblighiamo ad avere un metodo dedicato nel service.
    """
    all_machines = service.list_all_machines()  # deve restituire almeno: id, code, name, department_id (se disponibile)
    # Se nel record non c'è department_id, non filtro (mostro tutto).
    filtered = [m for m in all_machines if (("department_id" in m and m["department_id"] == dept_id) or ("department_id" not in m))]
    return filtered

# =========================
# HOME OPERATORI
# =========================
@view_router.get("/home-operators", response_class=HTMLResponse, include_in_schema=False)
async def home_operators(
    request: Request,
    current_user: TokenData = Depends(get_current_employee),
):
    return templates.TemplateResponse(
        "home_operators.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
        },
    )

# =========================
# PAGINA STAMPA (Mod. 021 S)
# =========================
@view_router.get("/jobs/stampa", response_class=HTMLResponse, include_in_schema=False)
async def jobs_stampa_page(
    request: Request,
    date: str = Query(default=None),
    machine_id: int = Query(default=0),
    service: JobService = Depends(JobService),
    current_user: TokenData = Depends(get_current_employee),
):
    if not date:
        date = _today_str()

    # Macchine di reparto STAMPA (se manca department_id, mostro tutte)
    machines = _machines_for_department(service, DEPT_STAMPA)

    data = []
    if machine_id:
        data = service.list_jobs_by_machine_and_date(date, machine_id)

    return templates.TemplateResponse(
        "jobs_stampa.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
            "selected_date": date,
            "selected_machine": machine_id or None,
            "machines": machines,
            "data": json.dumps(data, default=str),
        },
    )

# =========================
# PAGINA TAGLIO (Mod. 021 T)
# =========================
@view_router.get("/jobs/taglio", response_class=HTMLResponse, include_in_schema=False)
async def jobs_taglio_page(
    request: Request,
    date: str = Query(default=None),
    machine_id: int = Query(default=0),
    service: JobService = Depends(JobService),
    current_user: TokenData = Depends(get_current_employee),
):
    if not date:
        date = _today_str()

    # Macchine di reparto TAGLIO
    machines = _machines_for_department(service, DEPT_TAGLIO)

    data = []
    if machine_id:
        data = service.list_jobs_by_machine_and_date(date, machine_id)

    return templates.TemplateResponse(
        "jobs_taglio.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
            "selected_date": date,
            "selected_machine": machine_id or None,
            "machines": machines,
            "data": json.dumps(data, default=str),
        },
    )

# =========================
# PAGINA ACCOPPIAMENTO (Mod. 021 A)
# =========================
@view_router.get("/jobs/accoppiamento", response_class=HTMLResponse, include_in_schema=False)
async def jobs_accoppiamento_page(
    request: Request,
    date: str = Query(default=None),
    machine_id: int = Query(default=0),
    service: JobService = Depends(JobService),
    current_user: TokenData = Depends(get_current_employee),
):
    if not date:
        date = _today_str()

    # Macchine di reparto ACCOPPIAMENTO
    machines = _machines_for_department(service, DEPT_ACCO)

    data = []
    if machine_id:
        data = service.list_jobs_by_machine_and_date(date, machine_id)

    return templates.TemplateResponse(
        "jobs_accoppiamento.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
            "selected_date": date,
            "selected_machine": machine_id or None,
            "machines": machines,
            "data": json.dumps(data, default=str),
        },
    )

# =========================
# DETTAGLIO JOB (comune)
# =========================
@view_router.get("/jobs/detail/{job_id}", response_class=HTMLResponse, include_in_schema=False)
async def job_detail_page(
    request: Request,
    job_id: int,
    service: JobService = Depends(JobService),
    current_user: TokenData = Depends(get_current_employee),
):
    # Il template JS farà la fetch a /api/jobs/detail?job_id=...
    return templates.TemplateResponse(
        "job_detail.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
            "job_id": job_id,
        },
    )

# =========================
# DASHBOARD MANAGER
# =========================
@view_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_manager(
    request: Request,
    date: str = Query(default=None),
    current_user: TokenData = Depends(get_current_manager),  # solo HR/CEO
):
    if not date:
        date = _today_str()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "layout": "layout_manager.html",
            "selected_date": date,
        },
    )

# =========================
# BACKWARD COMPATIBILITY
# =========================
@view_router.get("/jobs", response_class=HTMLResponse, include_in_schema=False)
async def jobs_page_legacy_redirect(
    request: Request,
    date: str = Query(default=None),
    machine_id: int = Query(default=0),
    current_user: TokenData = Depends(get_current_employee),
):
    """
    Manteniamo la rotta /jobs per retro-compatibilità: rimanda alla home operatori
    da cui l'utente sceglie il reparto.
    Se vuoi, puoi cambiare il redirect verso /jobs/stampa.
    """
    return RedirectResponse(url="/home-operators")
