from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr

Category = Enum(
    value='Category',
    names=[
        ('symbols', 'symbols'),
        ('letters', 'letters'),
        ('numbers', 'numbers'),
        ('on-paper', 'on-paper'),
    ]
)


# User
class UserBase(BaseModel):
    email: str
    photo: Optional[str] = None
    is_active: Optional[bool] = None


class UserRegister(UserBase):
    name: str
    password: str
    password_confirmation: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    name: str
    password: str


class UserProtected(UserBase):
    id: int
    name: str


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    new_password_confirmation: str


# Token
class Token(BaseModel):
    token: str
    type: str


class TokenDecoded(BaseModel):
    email: Optional[str] = None


# Auth
class Auth(BaseModel):
    user: UserProtected
    token: Token

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


class StageProtected(StageBase):
    id: int

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
    stage_id: int


class AttemptedStageCreate(AttemptedStageBase):
    pass


class AttemptedStageProtected(AttemptedStageBase):
    id: int
    stage: StageProtected
    score: int
    question_count: int
    # attempted_questions: List[AttemptedQuestionProtected]  # For Score page

    class Config:
        orm_mode = True


class AttemptedStage(AttemptedStageBase):
    id: int
    stage: StageProtected
    attempted_questions: List[AttemptedQuestionProtected]  # For Score page
    score: int
    question_count: int

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
