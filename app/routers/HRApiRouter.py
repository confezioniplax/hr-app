from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Form
from fastapi.responses import JSONResponse

from app.dependencies import TokenData, get_current_manager
from app.services.HRService import HRService

hr_api_router = APIRouter(prefix="/api", tags=["hr-api"])

# -------- ANAGRAFICA --------
@hr_api_router.get("/hr/operators/list")
async def hr_list_operators(
    q: Optional[str] = Query(default=None),
    department_id: Optional[int] = Query(default=None),
    active: Optional[int] = Query(default=None),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        data = service.list_operator_core(q=q, department_id=department_id, active=active)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing operators: {str(e)}")

@hr_api_router.get("/hr/operators")
async def hr_list_operators_light(
    active: Optional[int] = Query(default=1),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        data = service.list_operators_light(active=active)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing operators: {str(e)}")

@hr_api_router.get("/hr/operators/{op_id}")
async def hr_get_operator(
    op_id: int,
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        op = service.get_operator(op_id)
        if not op:
            raise HTTPException(status_code=404, detail="Operator not found")
        return JSONResponse(status_code=200, content=op)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading operator: {str(e)}")

# -------- CREATE / UPDATE OPERATORE --------
@hr_api_router.post("/hr/operators/create")
async def hr_create_operator(
    first_name: str = Form(...),
    last_name: str = Form(...),
    fiscal_code: Optional[str] = Form(default=None),
    phone: Optional[str] = Form(default=None),
    email: Optional[str] = Form(default=None),
    address: Optional[str] = Form(default=None),
    birth_date: Optional[str] = Form(default=None),
    citizenship: Optional[str] = Form(default=None),
    education_level: Optional[str] = Form(default=None),
    hire_date: Optional[str] = Form(default=None),
    contract_type: Optional[str] = Form(default=None),
    contract_expiry: Optional[str] = Form(default=None),
    level: Optional[str] = Form(default=None),
    ral: Optional[str] = Form(default=None),
    departments: Optional[str] = Form(default=None),  # "REP1; REP2" (provvisorio)
    active: Optional[int] = Form(default=1),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        new_id = service.create_operator(
            first_name=first_name,
            last_name=last_name,
            fiscal_code=fiscal_code,
            phone=phone,
            email=email,
            address=address,
            birth_date=birth_date,

            # 👇 PASSA I NUOVI CAMPI
            citizenship=citizenship,
            education_level=education_level,

            hire_date=hire_date,
            contract_type=contract_type,
            contract_expiry=contract_expiry,
            level=level,
            ral=ral,
            departments=departments,
            active=active,
        )
        return JSONResponse(status_code=200, content={"message": "Operator created", "id": new_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating operator: {str(e)}")


@hr_api_router.post("/hr/operators/update")
async def hr_update_operator(
    id: int = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    fiscal_code: Optional[str] = Form(default=None),
    phone: Optional[str] = Form(default=None),
    birth_date: Optional[str] = Form(default=None),

    # 👇 NUOVI CAMPI
    citizenship: Optional[str] = Form(default=None),
    education_level: Optional[str] = Form(default=None),

    hire_date: Optional[str] = Form(default=None),
    contract_type: Optional[str] = Form(default=None),
    contract_expiry: Optional[str] = Form(default=None),
    level: Optional[str] = Form(default=None),
    ral: Optional[str] = Form(default=None),
    email: Optional[str] = Form(default=None),
    address: Optional[str] = Form(default=None),
    departments: Optional[str] = Form(default=None),
    active: Optional[int] = Form(default=1),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        service.update_operator(
            id=id,
            first_name=first_name,
            last_name=last_name,
            fiscal_code=fiscal_code,
            phone=phone,
            birth_date=birth_date,

            # 👇 PASSA I NUOVI CAMPI
            citizenship=citizenship,
            education_level=education_level,

            hire_date=hire_date,
            contract_type=contract_type,
            contract_expiry=contract_expiry,
            level=level,
            ral=ral,
            email=email,
            address=address,
            departments=departments,
            active=active,
        )
        return JSONResponse(status_code=200, content={"message": "Operator updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating operator: {str(e)}")

# -------- META --------
@hr_api_router.get("/hr/meta/cert-types")
async def hr_list_cert_types(
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        types = service.list_cert_types()
        return JSONResponse(status_code=200, content=types)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cert types: {str(e)}")

@hr_api_router.get("/hr/meta/departments")
async def hr_list_departments(
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        deps = service.list_departments()
        return JSONResponse(status_code=200, content=deps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing departments: {str(e)}")

# -------- CERTIFICAZIONI --------
@hr_api_router.get("/hr/certs/status")
async def hr_list_cert_status(
    department_id: Optional[int] = Query(default=None),
    cert_type_id: Optional[int] = Query(default=None),
    status_calc: Optional[str] = Query(default=None),
    operator_id: Optional[int] = Query(default=None),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        data = service.list_cert_status(
            department_id=department_id,
            cert_type_id=cert_type_id,
            status_calc=status_calc,
            operator_id=operator_id,
        )
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cert status: {str(e)}")

@hr_api_router.post("/hr/certs/upsert")
async def hr_upsert_cert(
    id: Optional[int] = Form(default=None),
    operator_id: int = Form(...),
    cert_type_id: int = Form(...),
    status: str = Form(...),
    issue_date: Optional[str] = Form(default=None),
    expiry_date: Optional[str] = Form(default=None),
    notes: Optional[str] = Form(default=None),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        cert_id = service.upsert_certification(
            id=id,
            operator_id=operator_id,
            cert_type_id=cert_type_id,
            status=status,
            issue_date=issue_date,
            expiry_date=expiry_date,
            notes=notes,
        )
        return JSONResponse(status_code=200, content={"message": "Certification saved", "id": cert_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving certification: {str(e)}")

@hr_api_router.post("/hr/certs/delete")
async def hr_delete_cert(
    id: int = Form(...),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        service.delete_certification(id)
        return JSONResponse(status_code=200, content={"message": "Certification deleted"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting certification: {str(e)}")

# -------- KPI --------
@hr_api_router.get("/hr/kpi")
async def hr_kpi(
    department_id: Optional[int] = Query(default=None),
    cert_type_id: Optional[int] = Query(default=None),
    status_calc: Optional[str] = Query(default=None),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    try:
        data = service.get_kpi(department_id=department_id, cert_type_id=cert_type_id, status_calc=status_calc)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing KPI: {str(e)}")


@hr_api_router.post("/hr/certs/types/create")
async def hr_create_cert_type(
    code: str = Form(...),
    description: Optional[str] = Form(default=None),
    requires_expiry: int = Form(default=1),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    # solo HR e CEO possono creare tipi certificazione
    if current_user.role not in ("HR", "CEO"):
        raise HTTPException(status_code=403, detail="Non autorizzato a creare tipi di certificazione")
    try:
        from app.db.db import DbManager, MySQLDb, QueryType
        with DbManager(MySQLDb()) as db:
            sql = """
                INSERT INTO operator_cert_types (code, description, requires_expiry)
                VALUES (%s, %s, %s)
            """
            db.execute_query(sql, [code.strip(), description or None, int(requires_expiry)], query_type=QueryType.INSERT)
        return JSONResponse(status_code=200, content={"message": "Tipo certificazione creato"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore creazione tipo certificazione: {str(e)}")
