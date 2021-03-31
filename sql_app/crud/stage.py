from typing import Optional

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from .. import models, schemas

# Stage
def get_stages(db: Session, user: schemas.UserProtected, category: Optional[str] = None, skip: int = 0, limit: int = 100):
    db_stages = db.query(models.Stage)

    if category:
        db_stages = db_stages.filter(models.Stage.category == category)

    db_stages = db_stages.offset(skip).limit(limit).all()

    if not db_stages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Stages not found")

    return db_stages
