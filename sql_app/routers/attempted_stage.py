from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()


# Attempted Stage
@router.get('/attempted-stages/{id}', response_model=schemas.AttemptedStage)
def read_attempted_stage(id: int, db: Session = Depends(dependencies.get_db), logged_in_user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    attempted_stage = crud.attempted_stage.get_attempted_stage(
        db, logged_in_user, id)

    return attempted_stage


@router.post('/attempted-stages/')
def create_attempted_stage(attempted_stage: schemas.AttemptedStageCreate, db: Session = Depends(dependencies.get_db), logged_in_user: schemas.UserProtected = Depends(dependencies.get_logged_in_user)):
    attempted_stage = crud.attempted_stage.create_attempted_stage(
        db, logged_in_user, attempted_stage)

    return attempted_stage
