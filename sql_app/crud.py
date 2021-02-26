from typing import List

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from . import models, schemas

# Test Question
# def get_test_questions(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.TestQuestion).offset(skip).limit(limit).all()

# Test Attempt
def create_test_attempt(db: Session, test_attempt: schemas.TestAttemptCreate):
    test_questions = db.query(models.TestQuestion.id).order_by(func.rand()).offset(0).limit(test_attempt.question_count)

    if test_questions.count() == 0:
        raise HTTPException(status_code=400, detail="Test questions are empty")
    if test_questions.count() < test_attempt.question_count:
        raise HTTPException(status_code=400, detail="Test questions are insufficient")

    db_test_attempt = models.TestAttempt(**test_attempt.dict())

    # Create test attempt
    db.add(db_test_attempt)
    db.commit()
    db.refresh(db_test_attempt)

    if db_test_attempt.id:
        # Get (random) attempted test questions from test questions table
        db_attempted_questions = list(models.AttemptedTestQuestion(test_question_id = test_question[0], test_attempt_id = db_test_attempt.id) for test_question in test_questions.all())

        # Create attempted test questions
        db.add_all(db_attempted_questions)
        db.commit()
        # db.refresh(db_attempted_questions)

        return db_test_attempt

def get_test_attempts(db: Session, skip: int = 1, limit: int = 100):
    db_test_attempt = db.query(models.TestAttempt).offset(skip).limit(limit).all()
    
    if db_test_attempt is None:
        raise HTTPException(status_code=404, detail="Test attempts are not found")
    
    return db_test_attempt

def get_test_attempt(db: Session, test_attempt_id: int):
    db_test_attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == test_attempt_id).first()
    
    if db_test_attempt is None:
        raise HTTPException(status_code=404, detail="Test attempt is not found")
    
    return db_test_attempt

# Attempted Test Question
def get_attempted_test_question(db: Session, test_attempt_id: int, page: int = 1):
    db_attempted_test_questions = db.query(models.AttemptedTestQuestion).filter(models.AttemptedTestQuestion.test_attempt_id == test_attempt_id)

    if db_attempted_test_questions.count() < page:
        raise HTTPException(status_code=404, detail="Attempted test question are not found")

    return db_attempted_test_questions[page-1]
    