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
@app.get('/stages/', response_model = List[schemas.Stage])
def read_stages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stages = crud.get_stages(db, skip, limit)
    return stages

@app.get('/stages/{type}', response_model = List[schemas.Stage])
def read_stages_by_type(type: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stages = crud.get_stages_by_type(db, type, skip, limit)
    return stages
    
# @app.get('/stages/{type}/{id}', response_model = schemas.Stage)
# def read_stage(id: int, type: str, db: Session = Depends(get_db)):
#     stage = crud.get_stage(db, id, type)
#     return stage

# Test Question
# @app.get('/test-questions/', response_model = List[schemas.TestQuestion])
# def read_test_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     test_questions = crud.get_test_questions(db, skip = skip, limit = limit)
#     return test_questions

# # Test Attempt
# @app.post('/tests/', response_model = schemas.TestAttempt)
# def create_test_attempt(test_attempt: schemas.TestAttemptCreate, db: Session = Depends(get_db)):
#     test_attempt = crud.create_test_attempt(db, test_attempt)
#     return test_attempt

# @app.get('/tests/', response_model = List[schemas.TestAttempt])
# def read_test_attempts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     test_attempts = crud.get_test_attempts(db, skip, limit)
#     return test_attempts

# @app.get('/tests/{test_attempt_id}/', response_model = schemas.TestAttempt)
# def read_test_attempt(test_attempt_id: int, db: Session = Depends(get_db)):
#     test_attempt = crud.get_test_attempt(db, test_attempt_id)
#     return test_attempt

# # Attempted Test Question
# @app.get('/tests/{test_attempt_id}/{page}', response_model = schemas.AttemptedTestQuestion)
# def read_attempted_test_question(test_attempt_id: int, page: int = Path(1, gt = 0), db: Session = Depends(get_db)):
#     attempted_test_question = crud.get_attempted_test_question(db, test_attempt_id, page)    
#     return attempted_test_question