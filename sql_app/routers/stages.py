from typing import List

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

# from .. import dependencies, crud, schemas
from ..dependencies import get_db
from ..crud import get_stages
from ..schemas import Stage

router = APIRouter()

# Stage
@router.get('/stages/category/{category}', response_model=List[Stage])
def read_stages_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stages = get_stages(db=db, category=category, skip=skip, limit=limit)

    return stages