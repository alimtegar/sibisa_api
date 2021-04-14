from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from .. import models, schemas


# Attempted Question
def get_attempted_question(db: Session, logged_in_user: schemas.UserProtected, id: int, n: int):
    db_attempted_questions = db.query(models.AttemptedQuestion).filter(
        models.AttemptedQuestion.attempted_stage_id == id)

    if db_attempted_questions.count() < n:
        raise HTTPException(
            status_code=404, detail="Attempted question not found")

    db_attempted_question = db_attempted_questions[n-1]

    if db_attempted_question.attempted_stage.user_id != logged_in_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Attempted question does not belong to user")

    return db_attempted_question


def update_attempted_question(db: Session, user: schemas.UserProtected, id: int, attempted_question: schemas.AttemptedQuestionUpdate):
    db_attempted_question = db.query(models.AttemptedQuestion).get(id)

    if not db_attempted_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Attempted question not found")

    if db_attempted_question.attempted_stage.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Attempted question does not belong to user")

    if db_attempted_question.answer:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Attempted question answer cannot be changed if it has been answered")


    is_correct = db_attempted_question.question.question == attempted_question.answer

    db_attempted_question.answer = attempted_question.answer
    db_attempted_question.is_correct = is_correct

    db.commit()
    
    if (is_correct):
        db_attempted_stage = db.query(models.AttemptedStage).get(db_attempted_question.attempted_stage_id)
        db_attempted_stage.score += 1 / db_attempted_stage.question_count * 100
        
        db.commit()
        
    db.refresh(db_attempted_question)

    return db_attempted_question
