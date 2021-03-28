from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()

# Token
@router.post('/token', response_model=schemas.Token)
def read_token_with_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    token = crud.get_token_with_form(db, form_data)

    return token

# User
@router.post('/register', response_model=schemas.UserProtected)
def create_user(user: schemas.UserRegister, db: Session = Depends(dependencies.get_db)):
    user = crud.create_user(db, user)

    return user

@router.post('/login', response_model=schemas.Token)
def read_user(user: schemas.UserLogin, db: Session = Depends(dependencies.get_db)):
    token = crud.get_token(db, user)

    return token

@router.get('/profile', response_model=schemas.UserProtected)
def read_logged_in_user(user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    return user
  