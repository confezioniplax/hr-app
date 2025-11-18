from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

from app.dependencies import TokenData, get_current_manager
from app.services.HRService import HRService
from app.services.CompanyDocsService import CompanyDocsService  # nuovo service

hr_api_router = APIRouter(prefix="/api", tags=["hr-api"])


# ==============================
#            HR
# ==============================

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
    departments: Optional[str] = Form(default=None),
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
    attachment: UploadFile | None = File(None),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Il salvataggio fisico e il naming (<TIPO>_<DATA>.<ext> sotto \\Certificazioni\\<CF>)
    li fa il Service. Qui leggiamo una sola volta il file e lo passiamo al service.
    """
    try:
        content = await attachment.read() if attachment and attachment.filename else None
        cert_id = service.upsert_certification(
            id=id,
            operator_id=operator_id,
            cert_type_id=cert_type_id,
            status=status,
            issue_date=issue_date,
            expiry_date=expiry_date,
            notes=notes,
            file_bytes=content,
            original_filename=attachment.filename if content else None,
        )
        return JSONResponse(status_code=200, content={"message": "Certification saved", "id": cert_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving certification: {str(e)}")


@hr_api_router.get("/hr/certs/download/{cert_id}")
async def hr_download_cert(
    cert_id: int,
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    row = service.get_certification(cert_id)
    path = (row or {}).get("file_path")
    if not path:
        raise HTTPException(status_code=404, detail="File non presente")
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File non trovato su disco")
    return FileResponse(p, filename=p.name)


@hr_api_router.get("/hr/certs/download-latest")
async def hr_download_cert_latest(
    operator_id: int = Query(...),
    cert_type_id: int = Query(...),
    service: HRService = Depends(HRService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Scarica SEMPRE l'ultima certificazione inserita per (operator_id, cert_type_id).
    La "più recente" è quella con id maggiore (se non è presente created_at).
    """
    row = service.get_latest_certification_for(operator_id=operator_id, cert_type_id=cert_type_id)
    if not row or not row.get("file_path"):
        raise HTTPException(status_code=404, detail="Nessun allegato trovato per l'ultima certificazione")
    p = Path(row["file_path"])
    if not p.exists():
        raise HTTPException(status_code=404, detail="File non trovato su disco")
    return FileResponse(p, filename=p.name)


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


# ==============================
#     DOCUMENTI AZIENDALI
# ==============================

def _to_int_or_none(v: Optional[str]) -> Optional[int]:
    if v is None:
        return None
    txt = str(v).strip()
    if txt == "":
        return None
    try:
        return int(txt)
    except Exception:
        return None  # tollera valori non numerici


@hr_api_router.get("/company-docs/list")
async def company_docs_list(
    q: Optional[str] = Query(default=None),
    year: Optional[str] = Query(default=None),        # accetta stringhe vuote
    frequency: Optional[str] = Query(default=None),   # può arrivare "" senza errori
    category: Optional[str] = Query(default=None),    # 👈 CODE categoria (es. 'ORG', 'DVR', 'ALTRO')
    service: CompanyDocsService = Depends(CompanyDocsService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Restituisce l'elenco dei documenti con filtri facoltativi.
    Tollerante a query come: ?q=&year=&frequency=&category=
    category = code FK su company_doc_categories.code (es. 'ORG', 'DISP', 'ALTRO')
    """
    try:
        year_int = _to_int_or_none(year)
        data = service.list_docs(
            q=(q or None),
            year=year_int,
            frequency=(frequency or None),
            category_code=(category or None),
        )
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing company documents: {str(e)}")


@hr_api_router.get("/company-docs/categories")
async def company_docs_categories(
    service: CompanyDocsService = Depends(CompanyDocsService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Restituisce la lista delle categorie disponibili da company_doc_categories.
    Usata dalla UI per popolare la tendina:
      - code
      - label
      - sort_order
    """
    try:
        cats = service.list_categories()
        return JSONResponse(status_code=200, content=cats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing company document categories: {str(e)}")


@hr_api_router.post("/company-docs/upsert")
async def company_docs_upsert(
    id: Optional[int] = Form(default=None),
    title: str = Form(...),
    year: int = Form(...),
    # 👇 IMPORTANTE: category ora è IL CODE (es. 'ORG','DVR','SORV_SAN','ALTRO')
    category: str = Form("ALTRO"),
    frequency: str = Form("annuale"),
    notes: Optional[str] = Form(default=None),
    attachment: UploadFile | None = File(None),
    service: CompanyDocsService = Depends(CompanyDocsService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Crea/aggiorna un documento aziendale.
    - category DEVE essere il codice FK su company_doc_categories.code (es. 'ORG', 'DVR', 'ALTRO').
    Il salvataggio fisico e il naming li fa il service, ad es.:
      <BASE>/DocumentiAziendali/<CATEGORY_CODE>/<YEAR>/<titolo_sanitizzato>_<anno>.<ext>
    In modifica, l'allegato è opzionale: se assente non cambia il file esistente.
    """
    try:
        file_bytes = await attachment.read() if attachment and attachment.filename else None
        doc_id = service.upsert_doc(
            id=id,
            title=title,
            year=year,
            category=category,  # code
            frequency=frequency,
            notes=notes,
            file_bytes=file_bytes,
            original_filename=attachment.filename if file_bytes else None,
        )
        return JSONResponse(status_code=200, content={"message": "Document saved", "id": doc_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving company document: {str(e)}")


@hr_api_router.get("/company-docs/download/{doc_id}")
async def company_docs_download(
    doc_id: int,
    service: CompanyDocsService = Depends(CompanyDocsService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Scarica l'allegato del documento.
    """
    row = service.get_doc(doc_id)
    path = (row or {}).get("file_path")
    if not path:
        raise HTTPException(status_code=404, detail="File non presente")
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File non trovato su disco")
    return FileResponse(p, filename=p.name)


@hr_api_router.post("/company-docs/delete")
async def company_docs_delete(
    id: int = Form(...),
    service: CompanyDocsService = Depends(CompanyDocsService),
    current_user: TokenData = Depends(get_current_manager),
):
    """
    Elimina un documento (solo record; il service può essere esteso per rimuovere anche il file fisico).
    """
    try:
        service.delete_doc(id)
        return JSONResponse(status_code=200, content={"message": "Document deleted"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting company document: {str(e)}")
