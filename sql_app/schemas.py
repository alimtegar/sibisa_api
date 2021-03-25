from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

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
    is_correct: Optional[bool]

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
    
    attempted_questions: List[AttemptedQuestionProtected] # For Score page
    
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