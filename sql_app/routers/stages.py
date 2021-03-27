from typing import List

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .. import dependencies, crud, schemas

router = APIRouter()


# Stage
@router.get('/stages/category/{category}', response_model=List[schemas.Stage])
def read_stages_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), user=Depends(dependencies.get_logged_in_user)):
    stages = crud.get_stages(
        db=db, user=user, category=category, skip=skip, limit=limit)

    return stages
