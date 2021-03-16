from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# Types
class Types(str, Enum):
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
    type: Types
    question_count: int

class Stage(StageBase):
    id: int
    questions: List[Question]
    
    class Config:
        orm_mode = True
        use_enum_values = True

# Attempted Question
class AttemptedQuestionBase(BaseModel):
    attempted_stage_id: int
    question_id: int
    answer: Optional[str]
    is_correct: Optional[bool]

class AttemptedQuestionCreate(AttemptedQuestionBase):
    pass

class AttemptedQuestion(AttemptedQuestionBase):
    id: int
    question: Question
    
    class Config:
        orm_mode = True

# Attempted Stage
class AttemptedStageBase(BaseModel):
    score: Optional[int]
    stage_id: int

class AttemptedStageCreate(AttemptedStageBase):
    pass

class AttemptedStage(AttemptedStageBase):
    id: int
    
    stage: Stage
    attempted_questions: List[AttemptedQuestion]
    
    class Config:
        orm_mode = True