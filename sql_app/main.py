from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import user, stage, attempted_stage, attempted_question
from .database import Base, engine

Base.metadata.create_all(bind=engine)

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

app.include_router(user.router)
app.include_router(stage.router)
app.include_router(attempted_stage.router)
app.include_router(attempted_question.router)

# Routes
# Home
@app.get('/')
def read_root():
    return {'Hello': 'World', }