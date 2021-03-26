from datetime import datetime, timedelta
from logging import disable
from typing import List, Optional
from random import shuffle

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import and_, or_, schema
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import JWTError, jwt

from . import models, schemas

# User


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(db, username: str):
    db_user = db.query(models.User).filter(
        models.User.username == username).first()
    
    if db_user:
        return schemas.User(username=db_user.username,
                            full_name=db_user.full_name,
                            email=db_user.email,
                            disabled=db_user.disabled)


def authenticate_user(db: Session, username: str, password: str):
    # user = get_user(fake_db, username)
    user = db.query(models.User).filter(
        models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(db: Session, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(db: Session, token: str):
    current_user = get_current_user(db, token)
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


def get_token_with_form(db, form_data: OAuth2PasswordRequestForm):
    user = authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


def get_token(db: Session, user: schemas.UserCreate):
    user = authenticate_user(
        db, user.username, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password)

    db.add(db_user)
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': db_user.username}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}

# Stage


def get_stages(db: Session, category: Optional[str] = None, skip: int = 0, limit: int = 100):
    db_stages = db.query(models.Stage)

    if category:
        db_stages = db_stages.filter(models.Stage.category == category)

    return db_stages.offset(skip).limit(limit).all()

# Attempted Stage


def get_attempted_stage(db: Session, id: int):
    db_attempted_stage = db.query(models.AttemptedStage).get(id)

    if not db_attempted_stage:
        raise HTTPException(
            status_code=404, detail="Attempted stage is not found")

    return db_attempted_stage


def create_attempted_stage(db: Session, attempted_stage: schemas.AttemptedStageCreate, id: int):
    questions = db.query(models.Question).filter(
        models.Question.stage_id == attempted_stage.stage_id)

    if questions.count() == 0:
        raise HTTPException(status_code=404, detail="Questions are empty")

    db_attempted_stage = models.AttemptedStage(**attempted_stage.dict())

    # Create attempted stage
    db.add(db_attempted_stage)
    db.commit()
    # db.refresh(db_attempted_stage)

    if db_attempted_stage.id:
        db_attempted_questions = [
            models.AttemptedQuestion(
                attempted_stage_id=db_attempted_stage.id,
                question_id=question.id)
            for question in questions.all()]
        # db_attempted_questions_random = [
        #     models.AttemptedQuestion(
        #         attempted_stage_id = db_attempted_stage.id,
        #         question_id = question.id)
        #         for question in questions.all()]

        shuffle(db_attempted_questions)

        # db_attempted_questions += db_attempted_questions_random

        # Create attempted test questions
        db.add_all(db_attempted_questions)
        db.commit()
        # db.refresh(db_attempted_questions)
        db.refresh(db_attempted_stage)

        return db_attempted_stage
    else:
        raise HTTPException(
            status_code=500, detail="Failed to create attempted stage")

# Attempted Question


def get_attempted_question(db: Session, id: int, n: int):
    db_attempted_questions = db.query(models.AttemptedQuestion).filter(
        models.AttemptedQuestion.attempted_stage_id == id)

    if db_attempted_questions.count() < n:
        raise HTTPException(
            status_code=404, detail="Attempted question is not found")

    return db_attempted_questions[n-1]


def update_attempted_question(db: Session, id: int, attempted_question: schemas.AttemptedQuestionUpdate):
    db_attempted_question = db.query(models.AttemptedQuestion).get(id)

    if not db_attempted_question:
        raise HTTPException(
            status_code=404, detail="Attempted question is not found")

    if db_attempted_question.answer:
        raise HTTPException(
            status_code=423, detail="Attempted question answer cannot be changed if it has been answered")

    db_attempted_question.answer = attempted_question.answer
    db_attempted_question.is_correct = db_attempted_question.question.question == attempted_question.answer

    db.commit()
    db.refresh(db_attempted_question)

    return db_attempted_question
