from random import shuffle

from fastapi import HTTPException, status

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


def create_attempted_stage(db: Session, logged_in_user: schemas.UserProtected, attempted_stage: schemas.AttemptedStageCreate):
    questions = db.query(models.Question).filter(
        models.Question.stage_id == attempted_stage.stage_id)

    if questions.count() == 0:
        raise HTTPException(status_code=404, detail="Questions are empty")

    db_attempted_stage = models.AttemptedStage(
        **attempted_stage.dict(), user_id=logged_in_user.id)

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