import shutil
import os
import uuid

from datetime import datetime, timedelta
from validate_email import validate_email

from fastapi import HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema

from sqlalchemy import and_
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
                                 photo=db_user.photo,
                                 is_active=db_user.is_active)


def validate_token(user: schemas.UserProtected):
    token = create_token(data={'sub': user.email})

    return {'user': user,
            'token': {'token': token,
                      'type': 'bearer'}}


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
        db, form_data.email, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email atau kata sandi salah.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    token = create_token(data={'sub': user.email})

    return {'token': token, 'type': 'bearer'}


def get_token(db: Session, user: schemas.UserLogin):
    user = authenticate_user(
        db, user.email, user.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email atau kata sandi salah.',
            headers={'WWW-Authenticate': 'Bearer'})

    if not user.is_active:
        raise HTTPException(
            status_code=400, detail='Pengguna belum diaktivasi.')

    token = create_token(data={'sub': user.email})

    return {'user': schemas.UserProtected(id=user.id,
                                          name=user.name,
                                          email=user.email,
                                          photo=user.photo,
                                          is_active=user.is_active),
            'token': {'token': token,
                      'type': 'bearer'}}


async def create_user(db: Session, fm: FastMail, user: schemas.UserRegister):
    # Validate inputs
    # Validate email
    is_valid = validate_email(email_address=user.email, check_smtp=False)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email tidak valid.')

    if user.password != user.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Kata sandi tidak cocok.')

    # Check if email is already registered or not
    db_user = db.query(models.User).filter(
        models.User.email == user.email).first()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email telah terdaftar.')

    # Hash password
    hashed_password = hash_password(user.password)

    db_user = models.User(name=user.name,
                          email=user.email,
                          password=hashed_password)

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

    return {'detail': 'Tautan aktivasi akun Sibisa anda telah dikirim via email.'}


def activate_user(db: Session, token: str):
    decoded_token = decode_token(token)

    db_user = db.query(models.User).filter(
        models.User.email == decoded_token.email).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token tidak valid',
                            headers={'WWW-Authenticate': 'Bearer'})

    if db_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token tidak valid',
                            headers={'WWW-Authenticate': 'Bearer'})

    db_user.is_active = 1

    db.commit()
    db.refresh(db_user)

    token = create_token(data={'sub': db_user.email})

    return {'user': schemas.UserProtected(id=db_user.id,
                                          name=db_user.name,
                                          email=db_user.email,
                                          photo=db_user.photo,
                                          is_active=db_user.is_active),
            'token': {'token': token,
                      'type': 'bearer'}}


def update_logged_in_user(db: Session, user: schemas.UserProtected, name: str, photo: UploadFile):
    db_user = db.query(models.User).filter(
        models.User.email == user.email).first()

    filedir = os.path.join('sql_app', 'images')

    # try:
    #     os.mkdir(filedir)
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                         detail='Terjadi kesalahan saat mengunggah foto profil')

    # return {'filename': photo.filename}

    # Name validation
    if (name):
        db_user.name = name
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Nama tidak boleh kosong.')

    # Photo validation
    if (photo):
        allowed_content_types = ['image/jpeg',
                                 'image/png', 'image/gif', 'image/svg+xml']
        if photo.content_type not in allowed_content_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Format file foto tidak didukung.')

        _, fileext = os.path.splitext(photo.filename)
        filename = uuid.uuid4().hex + fileext
        file = os.path.join(filedir, filename)

        with open(file, 'wb') as buffer:
            shutil.copyfileobj(photo.file, buffer)

        db_user.photo = filename
    else:
        db_user.photo = None

    db.commit()
    db.refresh(db_user)

    return schemas.UserProtected(id=db_user.id,
                                 name=db_user.name,
                                 email=db_user.email,
                                 photo=db_user.photo,
                                 is_active=db_user.is_active)


def update_user_password(db: Session, user: schemas.UserProtected, user_change_password: schemas.UserChangePassword):
    db_user = db.query(models.User).filter(
        and_(models.User.email == user.email, models.User.password == user_change_password.current_password)).first()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Kata sandi sekarang salah.')
        
    if user_change_password.new_password != user_change_password.new_password_confirmation:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Kata sandi baru tidak cocok.')        
        
    db_user.password = user_change_password.new_password
    
    db.commit()
    db.refresh(db_user)

    return {'detail': 'Kata sandi berhasil diubah.'}
