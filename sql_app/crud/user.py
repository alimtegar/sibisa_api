from datetime import datetime, timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from jose import JWTError, jwt

from .. import dependencies, models, schemas

settings = dependencies.get_settings()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_token(data: dict):
    expires_delta = timedelta(minutes=settings.token_expire_minutes)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.token_key, algorithm=settings.token_algorithm)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.token_key,
                             algorithms=[settings.token_algorithm])
        email: str = payload.get('sub')

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Token is invalid',
                                headers={'WWW-Authenticate': 'Bearer'})

        decoded_token = schemas.TokenDecoded(email=email)

        return decoded_token
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token is invalid',
                            headers={'WWW-Authenticate': 'Bearer'})


def get_user(db: Session, email: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    return schemas.UserProtected(id=db_user.id,
                                 email=db_user.email,
                                 name=db_user.name,
                                 is_active=db_user.is_active)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(
        models.User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_token_with_form(db, form_data: OAuth2PasswordRequestForm):
    user = authenticate_user(
        db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Username or password is incorrect',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    token = create_token(data={'sub': user.username})

    return {'token': token, 'type': 'bearer'}


def get_token(db: Session, user: schemas.UserLogin):
    user = authenticate_user(
        db, user.email, user.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Username or password is incorrect',
            headers={'WWW-Authenticate': 'Bearer'})

    if not user.is_active:
        raise HTTPException(status_code=400, detail='User is inactive')

    token = create_token(data={'sub': user.email})

    return {'token': token, 'type': 'bearer'}


async def create_user(db: Session, fm: FastMail, user: schemas.UserRegister):
    # Check if email is already registered or not
    db_user = db.query(models.User).filter(
        models.User.email == user.email).first()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email is already registered')

    # Hash password
    user.password = hash_password(user.password)

    db_user = models.User(**user.dict())

    db.add(db_user)
    db.commit()

    token = create_token(data={'sub': db_user.email})

    # Change this ASAP!!!
    activate_url = 'http://localhost:3000/activate/' + token
    html = f'<p>Klik <a href="{activate_url}">disini</a> untuk aktivasi akun Sibisa anda.</p>'

    message = MessageSchema(subject='Aktivasi Akun Sibisa',
                            recipients=[db_user.email],
                            html=html)

    await fm.send_message(message)

    return {'detail': 'Activation link has been sent via email'}


def activate_user(db: Session, token: str):
    decoded_token = decode_token(token)

    db_user = db.query(models.User).filter(
        models.User.email == decoded_token.email).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token is invalid',
                            headers={'WWW-Authenticate': 'Bearer'})

    if db_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token is invalid',
                            headers={'WWW-Authenticate': 'Bearer'})

    db_user.is_active = 1

    db.commit()
    db.refresh(db_user)

    return db_user
