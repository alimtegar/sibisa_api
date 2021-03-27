from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

# from .. import dependencies, crud, schemas
from ..dependencies import get_db, oauth2_scheme
from ..crud import get_token_with_form, get_token, create_user, get_logged_in_user
from ..schemas import Token, UserProtected, UserRegister, UserLogin

router = APIRouter()

# Token
@router.post('/token', response_model=Token)
def read_token_with_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = get_token_with_form(db, form_data)

    return token

# User
@router.post('/register', response_model=Token)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    user = create_user(db, user)

    return user

@router.post('/login', response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    token = get_token(db, user)

    return token

@router.get('/profile', response_model=UserProtected)
def read_logged_in_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    logged_in_user = get_logged_in_user(db, token)

    return logged_in_user
  