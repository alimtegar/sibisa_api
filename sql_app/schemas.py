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