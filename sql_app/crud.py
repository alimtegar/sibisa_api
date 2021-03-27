from datetime import datetime, timedelta
from typing import Optional
from random import shuffle

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import JWTError, jwt

from . import dependencies, models, schemas


# User
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials',
                                headers={'WWW-Authenticate': 'Bearer'})

        decoded_token = schemas.TokenDecoded(email=email)

        return decoded_token
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials',
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
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token = create_token(
        data={'sub': user.username}, expires_delta=token_expires
    )
    return {'token': token, 'type': 'bearer'}


def get_token(db: Session, user: schemas.UserLogin):
    user = authenticate_user(
        db, user.email, user.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')

    token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token = create_token(
        data={'sub': user.email}, expires_delta=token_expires
    )

    return {'token': token, 'type': 'bearer'}


def create_user(db: Session, user: schemas.UserRegister):
    # Check if email is already registered or not
    user = get_user(db, user.email)

    if user:
        raise HTTPException(
            status_code=409, detail='Email is already registered')

    # Hash password
    user.password = hash_password(user.password)

    db_user = models.User(**user.dict())

    db.add(db_user)
    db.commit()

    token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token = create_token(
        data={'sub': db_user.email}, expires_delta=token_expires
    )

    return {'token': token, 'type': 'bearer'}


# Stage
def get_stages(db: Session, user: schemas.UserProtected, category: Optional[str] = None, skip: int = 0, limit: int = 100):
    db_stages = db.query(models.Stage)

    if category:
        db_stages = db_stages.filter(models.Stage.category == category)

    db_stages = db_stages.offset(skip).limit(limit).all()

    if not db_stages:
        raise HTTPException(
            status_code=404, detail="Stages are not found")

    return db_stages


# Attempted Stage
def get_attempted_stage(db: Session, id: int):
    db_attempted_stage = db.query(models.AttemptedStage).get(id)

    if not db_attempted_stage:
        raise HTTPException(
            status_code=404, detail="Attempted stage is not found")

    return db_attempted_stage


def create_attempted_stage(db: Session, user: schemas.UserProtected, attempted_stage: schemas.AttemptedStageCreate):
    questions = db.query(models.Question).filter(
        models.Question.stage_id == attempted_stage.stage_id)

    if questions.count() == 0:
        raise HTTPException(status_code=404, detail="Questions are empty")

    db_attempted_stage = models.AttemptedStage(
        **attempted_stage.dict(), user_id=user.id)

    # Create attempted stage
    db.add(db_attempted_stage)
    db.commit()
    # db.refresh(db_attempted_stage)

    if db_attempted_stage.id:
        db_attempted_questions = [
            models.AttemptedQuestion(attempted_stage_id=db_attempted_stage.id,
                                     question_id=question.id)
            for question in questions.all()]

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
