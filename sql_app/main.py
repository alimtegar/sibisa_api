from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .routers import auth, stages, attempted_stages, attempted_questions
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*',
                   # 'http://localhost.tiangolo.com',
                   # # 'https://localhost.tiangolo.com',
                   # 'http://localhost',
                   # 'http://localhost:8080',
                   ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(stages.router)
app.include_router(attempted_stages.router)
app.include_router(attempted_questions.router)

# Routes
# Home
@app.get('/')
def read_root():
    return {'Hello': 'World', }