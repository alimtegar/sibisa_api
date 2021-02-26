from typing import List

from fastapi import Depends, FastAPI, HTTPException
# from fastapi.middleware.wsgi import WSGIMiddleware

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind = engine)

app = FastAPI()


# Depedency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def read_root():
    return {'Hello': 'World'}

# @app.get('/items/{item_id}')
# def read_item(item_id: int, q: Optional[str] = None):
#     return {'item_id': item_id, 'q': q}    

@app.post('/items/', response_model = schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = crud.create_item(db, item)
    return item

@app.get('/items/', response_model = List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip = skip, limit = limit)
    return items

# app.mount('/v1', WSGIMiddleware(app))