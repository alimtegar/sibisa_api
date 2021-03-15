import enum
from typing import List, Optional

from pydantic import BaseModel, Field

# Test Question
class TestQuestionBase(BaseModel):
    question: str

class TestQuestion(TestQuestionBase):
    id: int

    class Config:
        orm_mode = True

# Attempted Test Question
class AttemptedTestQuestionBase(BaseModel):
    answer: str

class AttemptedTestQuestion(AttemptedTestQuestionBase):
    id: int
    test_question_id: int
    test_question: TestQuestion
    # test_attempt_id: int
    # test_attempt: TestAttempt
    
    class Config:
        orm_mode = True

# Test Attempt
class TestAttemptBase(BaseModel):
    score: int
    question_count: int = Field(..., gt=0)

class TestAttemptCreate(TestAttemptBase):
    pass

class TestAttempt(TestAttemptBase):
    id: int
    attempted_test_questions: List[AttemptedTestQuestion]

    class Config:
        orm_mode = True

# Types
class Types(enum.Enum):
    SYMBOLS = 'symbols'
    LETTERS = 'letters'
    NUMBERS = 'numbers'

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
    type: Types
    question_count: int

class Stage(BaseModel):
    id: int
    questions: List[Question]
    
    class Config:
        orm_mode = True

# Attempted Question
class AttemptedQuestionBase(BaseModel):
    answer: str
    is_correct: bool

class AttemptedQuestion(AttemptedQuestionBase):
    id: int
    attempted_stage_id: int
    question_id: int
    question: Question
    
    class Config:
        orm_mode = True

# Attempted Stage
class AttemptedStageBase(BaseModel):
    score: int = Field(..., gt=0)

class AttemptedStage(AttemptedStageBase):
    id: int
    stage: Stage
    attempted_questions: List[AttemptedQuestion]
    
    class Config:
        orm_mode = True