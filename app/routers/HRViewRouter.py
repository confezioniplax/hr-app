from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import TokenData, get_current_manager
from app.services.HRService import HRService

hr_view_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def _layout_for(user: TokenData) -> str:
    return "layout_manager.html" if user.role in ("HR", "CEO") else "layout_employee.html"

# --- pagina legacy certificazioni ---
@hr_view_router.get("/hr/certificazioni", response_class=HTMLResponse, include_in_schema=False)
async def hr_certifications_page(
    request: Request,
    current_user: TokenData = Depends(get_current_manager),
    hr: HRService = Depends(HRService),
):
    try:
        departments = hr.list_departments()
    except Exception:
        departments = []
    try:
        cert_types = hr.list_cert_types()
    except Exception:
        cert_types = []

    return templates.TemplateResponse(
        "hr_certifications.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
            "departments": departments,
            "cert_types": cert_types,
            "operators_data": [],
            "certs_data": [],
        },
    )

# --- pagina dettaglio operatore ---
@hr_view_router.get("/hr/operators/{op_id}", response_class=HTMLResponse, include_in_schema=False)
async def hr_operator_detail_page(
    request: Request,
    op_id: int,
    current_user: TokenData = Depends(get_current_manager),
):
    return templates.TemplateResponse(
        "hr_operator_detail.html",
        {
            "request": request,
            "layout": _layout_for(current_user),
            "operator_id": op_id,
        },
    )
