from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()


# Attempted Stage
@router.get('/attempted-stages/{id}', response_model=schemas.AttemptedStage)
def read_attempted_stage(id: int, db: Session = Depends(dependencies.get_db), user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    attempted_stage = crud.get_attempted_stage(db=db, user=user, id=id)

    return attempted_stage


@router.post('/attempted-stages/')
def create_attempted_stage(attempted_stage: schemas.AttemptedStageCreate, db: Session = Depends(dependencies.get_db), user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    attempted_stage = crud.create_attempted_stage(
        db=db, user=user, attempted_stage=attempted_stage)

    return attempted_stage
