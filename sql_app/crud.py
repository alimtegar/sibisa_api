from typing import List
from random import shuffle

from fastapi import HTTPException

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from . import models, schemas

# Stage
def get_stages(db:Session, skip: int = 0, limit: int = 100):
    return db.query(models.Stage).offset(skip).limit(limit).all()

def get_stages_by_type(db:Session, type: str, skip: int = 0, limit: int = 100):
    return db.query(models.Stage).filter(models.Stage.type == type).offset(skip).limit(limit).all()

def create_attempted_stage(db: Session, attempted_stage: schemas.AttemptedStageCreate, id: int, type: str):
    questions = db.query(models.Question).filter(models.Question.stage_id == attempted_stage.stage_id)

    if questions.count() == 0:
        raise HTTPException(status_code = 404, detail = "Questions are empty")

    db_attempted_stage = models.AttemptedStage(**attempted_stage.dict())

    # Create attempted stage
    db.add(db_attempted_stage)
    db.commit()
    # db.refresh(db_attempted_stage)

    if db_attempted_stage.id:
        db_attempted_questions = [
            models.AttemptedQuestion(
                attempted_stage_id = db_attempted_stage.id,
                question_id = question.id)
                for question in questions.all()]
        db_attempted_questions_random = [
            models.AttemptedQuestion(
                attempted_stage_id = db_attempted_stage.id,
                question_id = question.id)
                for question in questions.all()]

        shuffle(db_attempted_questions_random)

        db_attempted_questions += db_attempted_questions_random
                
        # Create attempted test questions
        db.add_all(db_attempted_questions)
        db.commit()
        # db.refresh(db_attempted_questions)
        db.refresh(db_attempted_stage)

        return db_attempted_stage
    else:
        raise HTTPException(status_code = 500, detail = "Failed to create attempted stage")

def get_attempted_question(db: Session, id: int, page: int):
    db_attempted_questions = db.query(models.AttemptedQuestion).filter(models.AttemptedQuestion.attempted_stage_id == id)

    if db_attempted_questions.count() < page:
        raise HTTPException(status_code=404, detail="Attempted question is not found")

    return db_attempted_questions[page-1]


# def get_stage(db:Session, id: int, type: str):
#     return db.query(models.Stage).filter(and_(models.Stage.id == id, models.Stage.type == type)).first()

# Test Question
# def get_test_questions(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.TestQuestion).offset(skip).limit(limit).all()

# # Test Attempt
# def create_test_attempt(db: Session, test_attempt: schemas.TestAttemptCreate):
#     test_questions = db.query(models.TestQuestion.id).order_by(func.rand()).offset(0).limit(test_attempt.question_count)

#     if test_questions.count() == 0:
#         raise HTTPException(status_code=400, detail="Test questions are empty")
#     if test_questions.count() < test_attempt.question_count:
#         raise HTTPException(status_code=400, detail="Test questions are insufficient")

#     db_test_attempt = models.TestAttempt(**test_attempt.dict())

#     # Create test attempt
#     db.add(db_test_attempt)
#     db.commit()
#     db.refresh(db_test_attempt)

#     if db_test_attempt.id:
#         # Get (random) attempted test questions from test questions table
#         db_attempted_questions = list(models.AttemptedTestQuestion(test_question_id = test_question[0], test_attempt_id = db_test_attempt.id) for test_question in test_questions.all())

#         # Create attempted test questions
#         db.add_all(db_attempted_questions)
#         db.commit()
#         # db.refresh(db_attempted_questions)

#         return db_test_attempt

# def get_test_attempts(db: Session, skip: int = 1, limit: int = 100):
#     db_test_attempt = db.query(models.TestAttempt).offset(skip).limit(limit).all()
    
#     if db_test_attempt is None:
#         raise HTTPException(status_code=404, detail="Test attempts are not found")
    
#     return db_test_attempt

# def get_test_attempt(db: Session, test_attempt_id: int):
#     db_test_attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == test_attempt_id).first()
    
#     if db_test_attempt is None:
#         raise HTTPException(status_code=404, detail="Test attempt is not found")
    
#     return db_test_attempt

# # Attempted Test Question
# def get_attempted_test_question(db: Session, test_attempt_id: int, page: int = 1):
#     db_attempted_test_questions = db.query(models.AttemptedTestQuestion).filter(models.AttemptedTestQuestion.test_attempt_id == test_attempt_id)

#     if db_attempted_test_questions.count() < page:
#         raise HTTPException(status_code=404, detail="Attempted test question are not found")

#     return db_attempted_test_questions[page-1]
    