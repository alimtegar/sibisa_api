
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship

from .database import Base
from .schemas import Types

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

# Stage
class Stage(Base):
    __tablename__ = 'stages'

    id = Column(Integer, primary_key = True, index = True)
    type = Column(Enum(Types))
    question_count = Column(Integer)

    questions = relationship('Question', back_populates = 'stage')

# Question
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key = True, index = True)
    stage_id = Column(Integer, ForeignKey('stages.id'))
    question = Column(String(8))

    stage = relationship('Stage', back_populates = 'questions')

# Attempted Stage
class AttemptedStage(Base):
    __tablename__ = 'attempted_stages'

    id = Column(Integer, primary_key = True, index = True)
    stage_id = Column(Integer, ForeignKey('stages.id'))
    score = Column(Integer)

    stage = relationship('Stage', back_populates = 'attempted_stages')
    attempted_questions = relationship('AttemptedQuestion', back_populates = 'attempted_stage')

# Attempted Question
class AttemptedQuestion(Base):
    __tablename__ = 'attempted_questions'

    id = Column(Integer, primary_key = True, index = True)
    attempted_stage_id = Column(Integer, ForeignKey('attempted_stages.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer = Column(String(255))
    is_correct = Column(Boolean)

    attempted_stage = relationship('AttemptedStage', back_populates = 'attempted_question')
    question = relationship('Question', back_populates = 'attempted_questions')