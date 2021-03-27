from fastapi.security import OAuth2PasswordBearer

from .database import SessionLocal

# Depedencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
