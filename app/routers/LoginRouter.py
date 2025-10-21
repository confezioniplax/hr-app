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

from datetime import timedelta, datetime
from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse, Response
from app.model.PersonModel import PersonModel
from app.entities.Person import Person
from app.dependencies import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
  prefix="/token",
  tags=["login"]
)

@router.post("/")
def get_auth_token(response: Response, request: Request, background_task: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends(), language: str | None = Header(default='it')):
    user_model = PersonModel()
    user: Person = user_model.get_user_info_auth(form_data.username)
    
    if not user:
        return JSONResponse(
            status_code=401,
            content="user_not_found",
            headers={"WWW-Authenticate": "Bearer"},
        )        
    elif not user_model.check_password(stored_password=user.user_password, password=form_data.password):
        return JSONResponse(
            status_code=401,
            content="username_password_error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=480)
    access_token = create_access_token(user.__dict__, expires_delta=access_token_expires)

    response.set_cookie(key="access_token", value=access_token, expires=int(access_token_expires.total_seconds()))


    response = JSONResponse(
        status_code=200,
        content={
            "message": "Login successful",
            "userdata": {"username": form_data.username, "role": user.role}
        }
    )
    response.set_cookie(key="access_token", value=access_token, expires=int(access_token_expires.total_seconds()))
    return response


@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response