from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# User
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserCreate(User):
    password: str

class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

# Category


class Category(str, Enum):
    symbols = 'symbols'
    letters = 'letters'
    numbers = 'numbers'

# Question


class QuestionBase(BaseModel):
    question: str


class Question(QuestionBase):
    id: int
    stage_id: int

    class Config:
        orm_mode = True

# Stage


class StageBase(BaseModel):
    stage: str
    category: Category
    question_count: int


class StageProtected(StageBase):
    pass

    class Config:
        orm_mode = True
        # use_enum_values = True


class Stage(StageBase):
    id: int
    questions: List[Question]

    class Config:
        orm_mode = True
        # use_enum_values = True

# Attempted Stage


class AttemptedQuestionBase(BaseModel):
    answer: Optional[str]       # Updatable


class AttemptedQuestionProtected(AttemptedQuestionBase):
    id: int
    is_correct: Optional[bool]
    question: Question

    class Config:
        orm_mode = True


class AttemptedStageBase(BaseModel):
    score: Optional[int]
    stage_id: int


class AttemptedStageCreate(AttemptedStageBase):
    pass


class AttemptedStageProtected(AttemptedStageBase):
    stage: StageProtected

    class Config:
        orm_mode = True


class AttemptedStage(AttemptedStageBase):
    id: int
    stage: StageProtected
    attempted_questions: List[AttemptedQuestionProtected]  # For Score page

    class Config:
        orm_mode = True

# Attempted Question


class AttemptedQuestionCreate(AttemptedQuestionBase):
    attempted_stage_id: int
    question_id: int
    is_correct: Optional[bool]


class AttemptedQuestionUpdate(AttemptedQuestionBase):
    pass


class AttemptedQuestion(AttemptedQuestionBase):
    id: int
    attempted_stage_id: int
    attempted_stage: AttemptedStageProtected
    question_id: int
    question: Question

    class Config:
        orm_mode = True
