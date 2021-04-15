from random import shuffle

from fastapi import HTTPException, status

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from .. import models, schemas

# Attempted Stage


def get_attempted_stage(db: Session, logged_in_user: schemas.UserProtected, id: int):
    db_attempted_stage = db.query(models.AttemptedStage).get(id)

    if not db_attempted_stage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Attempted stage not found")

    if db_attempted_stage.user_id != logged_in_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Attempted stage does not belong to user")

    return db_attempted_stage


def get_attempted_stages(db: Session, logged_in_user: schemas.UserProtected, skip: int = 0, limit: int = 100):
    db_attempted_stages = db.query(models.AttemptedStage).order_by(models.AttemptedStage.id.desc()).filter(
        models.AttemptedStage.user_id == logged_in_user.id).offset(skip).limit(limit).all()

    if not db_attempted_stages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Attempted stages not found")

    return db_attempted_stages


def get_best_attempted_stage(db: Session, logged_in_user: schemas.UserProtected, category: str, stage: int):
    db_stage = db.query(models.Stage).filter(
        and_(models.Stage.category == category, models.Stage.stage == stage)).first()

    if not db_stage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Stage not found")

    user_id = logged_in_user.id
    stage_id = db_stage.id

    max_score = db.query(func.max(models.AttemptedStage.score)).filter(and_(
        models.AttemptedStage.user_id == user_id, models.AttemptedStage.stage_id == stage_id))

    db_attempted_stage = db.query(models.AttemptedStage).filter(and_(
        models.AttemptedStage.user_id == user_id, models.AttemptedStage.stage_id == stage_id, models.AttemptedStage.score == max_score)).first()

    return db_attempted_stage


def create_attempted_stage(db: Session, logged_in_user: schemas.UserProtected, attempted_stage: schemas.AttemptedStageCreate):
    questions = db.query(models.Question).filter(
        models.Question.stage_id == attempted_stage.stage_id)

    if questions.count() == 0:
        raise HTTPException(status_code=404, detail="Questions are empty")

    db_attempted_stage = models.AttemptedStage(
        **attempted_stage.dict(), user_id=logged_in_user.id, question_count=questions.count())

    # Create attempted stage
    db.add(db_attempted_stage)
    db.commit()
    # db.refresh(db_attempted_stage)

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
