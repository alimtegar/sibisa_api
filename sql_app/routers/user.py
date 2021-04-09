from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_mail import FastMail

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()


# Token
@router.post('/token', response_model=schemas.Token)
def read_token_with_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    token = crud.user.get_token_with_form(db, form_data)

    return token


# User
@router.post('/register')
async def create_user(user: schemas.UserRegister, db: Session = Depends(dependencies.get_db), fm: FastMail = Depends(dependencies.get_fm)):
    user = await crud.user.create_user(db, fm, user)

    return user


@router.post('/login', response_model=schemas.Auth)
def read_user(user: schemas.UserLogin, db: Session = Depends(dependencies.get_db)):
    token = crud.user.get_token(db, user)

    return token


@router.get('/profile', response_model=schemas.UserProtected)
def read_logged_in_user(logged_in_user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return logged_in_user


@router.get('/activate/{token}', response_model=schemas.Auth)
def activate_user(token: str, db: Session = Depends(dependencies.get_db)):
    return crud.user.activate_user(db, token)


@router.get('/validate-token', response_model=schemas.Auth)
def validate_token(logged_in_user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return crud.user.validate_token(logged_in_user)


@router.put('/profile', response_model=schemas.UserProtected)
def update_user(name: str = Form(...), photo: Optional[UploadFile] = File(None), db: Session = Depends(dependencies.get_db), logged_in_user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return crud.user.update_user(db, logged_in_user, name, photo)

@router.put('/profile/password')
def update_user_password(user: schemas.UserChangePassword, db: Session = Depends(dependencies.get_db), logged_in_user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return crud.user.update_user_password(db, logged_in_user, user)