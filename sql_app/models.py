
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship

from .database import Base
from .schemas import Category

# User

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16), unique=True, index=True)
    full_name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(64))
    disabled = Column(Boolean)

# Stage


class Stage(Base):
    __tablename__ = 'stages'

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(Integer, index=True)
    category = Column(Enum(Category), index=True)
    question_count = Column(Integer)

    questions = relationship('Question', back_populates='stage')
    attempted_stages = relationship('AttemptedStage', back_populates='stage')

# Question


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey('stages.id'))
    question = Column(String(8))

    stage = relationship('Stage', back_populates='questions')
    attempted_questions = relationship(
        'AttemptedQuestion', back_populates='question')

# Attempted Stage


class AttemptedStage(Base):
    __tablename__ = 'attempted_stages'

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey('stages.id'))
    score = Column(Integer, default=0)

    stage = relationship('Stage', back_populates='attempted_stages')
    attempted_questions = relationship(
        'AttemptedQuestion', back_populates='attempted_stage')

# Attempted Question


class AttemptedQuestion(Base):
    __tablename__ = 'attempted_questions'

    id = Column(Integer, primary_key=True, index=True)
    attempted_stage_id = Column(Integer, ForeignKey('attempted_stages.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer = Column(String(255))
    is_correct = Column(Boolean)

    attempted_stage = relationship(
        'AttemptedStage', back_populates='attempted_questions')
    question = relationship('Question', back_populates='attempted_questions')
