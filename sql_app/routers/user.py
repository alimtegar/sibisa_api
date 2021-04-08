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
def read_logged_in_user(user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return user


@router.get('/activate/{token}', response_model=schemas.Auth)
def activate_user(token: str, db: Session = Depends(dependencies.get_db)):
    return crud.user.activate_user(db, token)


@router.get('/validate-token', response_model=schemas.Auth)
def validate_token(user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return crud.user.validate_token(user)


@router.put('/profile')
def update_logged_in_user(name: str = Form(...), photo: Optional[UploadFile] = File(None), db: Session = Depends(dependencies.get_db), user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return crud.user.update_logged_in_user(db, user, name, photo)
