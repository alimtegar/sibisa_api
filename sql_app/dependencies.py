from functools import lru_cache

from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

# Settings
from . import config

@lru_cache()
def get_settings():
    return config.Settings()

# Database
from . import database

async def get_db():
    db = await database.SessionLocal()
    
    try:
        yield db
    finally:
        db.close()

# Token
from . import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def get_logged_in_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    decoded_token = crud.decode_token(token)
    user = crud.get_user(db, email=decoded_token.email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User is not found',
                            headers={'WWW-Authenticate': 'Bearer'})
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail='User is inactive',
                            headers={'WWW-Authenticate': 'Bearer'})

    return user

# Database
from . import database

def get_db():
    db = database.SessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
# Email
from . import email

def get_fm():
    fm = email.fm
    
    return fm