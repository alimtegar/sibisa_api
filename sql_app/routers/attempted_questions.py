from fastapi import APIRouter, Depends, Path

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()


# Attempted Question
@router.get('/attempted-stages/{id}/attempted-questions/n/{n}', response_model=schemas.AttemptedQuestion)
def read_attempted_stage_question(id: int, n: int = Path(1, gt=0), db: Session = Depends(dependencies.get_db), user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    attempted_question = crud.get_attempted_question(
        db=db, user=user, id=id, n=n)

    return attempted_question


@router.put('/attempted-questions/{id}', response_model=schemas.AttemptedQuestionProtected)
def update_attempted_stage_question(id: int, attempted_question: schemas.AttemptedQuestionUpdate, db: Session = Depends(dependencies.get_db), user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    attempted_question = crud.update_attempted_question(
        db=db, user=user, id=id, attempted_question=attempted_question)

    return attempted_question
