from fastapi import APIRouter, Depends, Path

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()


# Attempted Question
@router.get('/attempted-stages/{id}/attempted-questions/n/{n}', response_model=schemas.AttemptedQuestion)
def read_attempted_stage_question(id: int, n: int = Path(1, gt=0), db: Session = Depends(dependencies.get_db)):
    attempted_question = crud.get_attempted_question(db, id, n)

    return attempted_question


@router.put('/attempted-questions/{id}', response_model=schemas.AttemptedQuestionProtected)
def update_attempted_stage_question(id: int, attempted_question: schemas.AttemptedQuestionUpdate, db: Session = Depends(dependencies.get_db)):
    attempted_question = crud.update_attempted_question(
        db, id, attempted_question)

    return attempted_question
