from typing import List

from fastapi import Depends, FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

origins = [
    "*",
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Depedency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def read_root():
    return {'Hello': 'World'}

# Stage
@app.get('/stages/category/{category}', response_model = List[schemas.Stage])
def read_stages_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stages = crud.get_stages(db = db, category = category, skip = skip, limit = limit)

    return stages

# Attempted Stage
@app.get('/attempted-stages/{id}' , response_model = schemas.AttemptedStage)
def read_attempted_stage(id: int, db: Session = Depends(get_db)):
    attempted_stage = crud.get_attempted_stage(db, id)

    return attempted_stage

@app.post('/attempted-stages/', response_model = schemas.AttemptedStage)
def create_attempted_stage(attempted_stage: schemas.AttemptedStageCreate, db: Session = Depends(get_db)):
    attempted_stage = crud.create_attempted_stage(db, attempted_stage, id)

    return attempted_stage

# Attempted Question
@app.get('/attempted-stages/{id}/attempted-questions/n/{n}', response_model = schemas.AttemptedQuestion)
def read_attempted_stage_question(id: int, n: int = Path(1, gt = 0), db: Session = Depends(get_db)):
    attempted_question = crud.get_attempted_question(db, id, n)

    return attempted_question

@app.put('/attempted-questions/{id}', response_model = schemas.AttemptedQuestionProtected)
def update_attempted_stage_question(id: int, attempted_question: schemas.AttemptedQuestionUpdate, db: Session = Depends(get_db)):
    attempted_question = crud.update_attempted_question(db, id, attempted_question)

    return attempted_question
