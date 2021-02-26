from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

# Test Question
class TestQuestion(Base):
    __tablename__ = 'test_questions'

    id = Column(Integer, primary_key = True, index = True)
    question = Column(String(32))

    attempted_test_questions = relationship('AttemptedTestQuestion', back_populates = 'test_question')

# Test Attempt
class TestAttempt(Base):
    __tablename__ = 'test_attempts'

    id = Column(Integer, primary_key = True, index = True)
    score = Column(Integer, default = 0)
    question_count = Column(Integer)

    attempted_test_questions = relationship('AttemptedTestQuestion', back_populates = 'test_attempt')

# Attempted Test Question
class AttemptedTestQuestion(Base):
    __tablename__ = 'attempted_test_questions'

    id = Column(Integer, primary_key = True, index = True)
    test_question_id = Column(Integer, ForeignKey('test_questions.id'))
    test_attempt_id = Column(Integer, ForeignKey('test_attempts.id'))

    answer = Column(String(32), default = '')

    test_question = relationship('TestQuestion', back_populates = 'attempted_test_questions')
    test_attempt = relationship('TestAttempt', back_populates = 'attempted_test_questions')