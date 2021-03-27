from typing import List

from fastapi import FastAPI, Depends, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic.schema import schema

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*',
                   # 'http://localhost.tiangolo.com',
                   # # 'https://localhost.tiangolo.com',
                   # 'http://localhost',
                   # 'http://localhost:8080',
                   ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Depedencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# Routes
# Home
@app.get('/')
def read_root():
    return {'Hello': 'World', }


# User
@app.post('/token', response_model=schemas.Token)
def read_token_with_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = crud.get_token_with_form(db, form_data)

    return token


@app.post('/register', response_model=schemas.Token)
def create_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    user = crud.create_user(db, user)

    return user

@app.post('/login', response_model=schemas.Token)
def read_token(user: schemas.UserLogin, db: Session = Depends(get_db)):
    token = crud.get_token(db, user)

    return token

@app.get('/profile', response_model=schemas.UserProtected)
def read_logged_in_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    logged_in_user = crud.get_logged_in_user(db, token)

    return logged_in_user

# Stage
@app.get('/stages/category/{category}', response_model=List[schemas.Stage])
def read_stages_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stages = crud.get_stages(db=db, category=category, skip=skip, limit=limit)

    return stages


# Attempted Stage
@app.get('/attempted-stages/{id}', response_model=schemas.AttemptedStage)
def read_attempted_stage(id: int, db: Session = Depends(get_db)):
    attempted_stage = crud.get_attempted_stage(db, id)

    return attempted_stage


@app.post('/attempted-stages/', response_model=schemas.AttemptedStage)
def create_attempted_stage(attempted_stage: schemas.AttemptedStageCreate, db: Session = Depends(get_db)):
    attempted_stage = crud.create_attempted_stage(db, attempted_stage, id)

    return attempted_stage


# Attempted Question
@app.get('/attempted-stages/{id}/attempted-questions/n/{n}', response_model=schemas.AttemptedQuestion)
def read_attempted_stage_question(id: int, n: int = Path(1, gt=0), db: Session = Depends(get_db)):
    attempted_question = crud.get_attempted_question(db, id, n)

    return attempted_question


@app.put('/attempted-questions/{id}', response_model=schemas.AttemptedQuestionProtected)
def update_attempted_stage_question(id: int, attempted_question: schemas.AttemptedQuestionUpdate, db: Session = Depends(get_db)):
    attempted_question = crud.update_attempted_question(
        db, id, attempted_question)

    return attempted_question
