from contextlib import asynccontextmanager
from datetime import timedelta
import datetime
import random
import string
import time
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.requests import Request
from fastapi import Security, Depends, FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.db import DbManager, MySQLDb, QueryType 
from .routers.ApiRouter import api_router
from .routers.LoginRouter import router
from .routers.ViewRouter import view_router
from .routers.HRApiRouter import hr_api_router
from .routers.HRViewRouter import hr_view_router

app = FastAPI(
    title="venue-access-app",
    description="Venue Access App",
    version="0.0.1",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="app/templates")

@app.middleware("http")
async def log_request(request: Request, call_next):
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    headers = request.headers
    return response

origins = [
    "*",
    "http://localhost:8080",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health", response_class=JSONResponse)
def db_health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=status.HTTP_200_OK)

@app.get("/health/db", response_class=JSONResponse)
def db_health_check():
    """
    Check the database connection by attempting to execute a simple query.
    Returns a JSON response with the status of the connection.
    """
    try:
        db_manager = DbManager(MySQLDb())
        with db_manager as db:
            # Executing a simple SELECT statement to check the database connection
            db.execute_query("SELECT 1", query_type=QueryType.GET)
        return JSONResponse(content={"status": "healthy"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"status": "unhealthy", "error": str(e)}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/login")
    if exc.status_code == 403:
        return RedirectResponse(url='/personal_presence')
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)
app.include_router(view_router)
app.include_router(router)
app.include_router(hr_api_router)
app.include_router(hr_view_router)