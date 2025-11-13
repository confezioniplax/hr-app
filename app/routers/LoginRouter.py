"""
 MIT License
 
 Copyright (c) 2024 Riccardo Leonelli
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""

from datetime import timedelta
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from app.model.PersonModel import PersonModel
from app.entities.Person import Person
from app.dependencies import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

# Servizio che invia l'email di scadenze
try:
    from app.services.HRService import HRService
except Exception:
    # fallback se il path è differente (es. HRService.py alla radice del progetto)
    from HRService import HRService  # type: ignore

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/token",
    tags=["login"]
)

@router.post("/")
def get_auth_token(
    response: Response,
    request: Request,
    background_task: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    language: str | None = Header(default='it')
):
    user_model = PersonModel()
    user: Person | None = user_model.get_user_info_auth(form_data.username)

    if not user:
        return JSONResponse(
            status_code=401,
            content="user_not_found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_model.check_password(stored_password=user.user_password, password=form_data.password):
        return JSONResponse(
            status_code=401,
            content="username_password_error",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT
    access_token_expires = timedelta(minutes=480)
    access_token = create_access_token(user.__dict__, expires_delta=access_token_expires)

    # Cookie
    response.set_cookie(key="access_token", value=access_token, expires=int(access_token_expires.total_seconds()))

    # Programma l’invio dell’email scadenze in background (non blocca il login)
    def _send_expiry_email_task(recipient: str):
        try:
            HRService().send_expiring_certs_email_if_needed(
                recipient_email=recipient,
                days=30,            # modifica qui la soglia se vuoi
                department_id=None  # oppure filtra per reparto del manager
            )
        except Exception as e:
            logger.warning(f"Expiry email not sent: {e}")

    # recipient_email = (getattr(user, "email", None) or "leonelliriccardo0@gmail.com").strip()
    recipients = [
    "p.pellegrini@plaxpackaging.it",
    "produzione@plaxpackaging.it",
    "f.fornasari@plaxpackaging.it",
    "marco@plaxpackaging.it",
    "riccardo@plaxpackaging.it"
    ]

    for email in recipients:
        background_task.add_task(_send_expiry_email_task, email)

    # Risposta API
    res = JSONResponse(
        status_code=200,
        content={
            "message": "Login successful",
            "userdata": {"username": form_data.username, "role": user.role}
        }
    )
    res.set_cookie(key="access_token", value=access_token, expires=int(access_token_expires.total_seconds()))
    return res


@router.get("/logout")
def logout(response: Response):
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp
