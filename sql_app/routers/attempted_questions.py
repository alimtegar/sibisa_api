from fastapi import APIRouter, Depends, Path

from sqlalchemy.orm import Session

# from .. import dependencies, crud, schemas
from ..dependencies import get_db
from ..crud import get_attempted_question, update_attempted_question
from ..schemas import AttemptedQuestion, AttemptedQuestionProtected, AttemptedQuestionUpdate

router = APIRouter()


# Attempted Question
@router.get('/attempted-stages/{id}/attempted-questions/n/{n}', response_model=AttemptedQuestion)
def read_attempted_stage_question(id: int, n: int = Path(1, gt=0), db: Session = Depends(get_db)):
    attempted_question = get_attempted_question(db, id, n)

    return attempted_question


@router.put('/attempted-questions/{id}', response_model=AttemptedQuestionProtected)
def update_attempted_stage_question(id: int, attempted_question: AttemptedQuestionUpdate, db: Session = Depends(get_db)):
    attempted_question = update_attempted_question(db, id, attempted_question)

    return attempted_question
