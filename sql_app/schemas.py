from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# Email
class EEmail(BaseModel):
   email: List[EmailStr]


# User
class UserBase(BaseModel):
    email: str
    is_active: Optional[bool] = None


class UserRegister(UserBase):
    name: str
    password: str
    password_confirmation: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    password: str


class UserProtected(UserBase):
    id: int
    name: str    


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
