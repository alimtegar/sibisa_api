from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..crud import get_attempted_stage
from ..schemas import AttemptedStage, AttemptedStageCreate

router = APIRouter()


# Attempted Stage
@router.get('/attempted-stages/{id}', response_model=AttemptedStage)
def read_attempted_stage(id: int, db: Session = Depends(get_db)):
    attempted_stage = get_attempted_stage(db, id)

    return attempted_stage


@router.post('/attempted-stages/', response_model=AttemptedStage)
def create_attempted_stage(attempted_stage: AttemptedStageCreate, db: Session = Depends(get_db)):
    attempted_stage = create_attempted_stage(db, attempted_stage, id)

    return attempted_stage
