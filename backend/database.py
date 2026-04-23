"""
Database models and connection setup for the Learning Path Recommendation System.
"""

import json
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///./learning_path.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

COURSE_TOTAL_PAGES = 5


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    skills = Column(Text, default="[]")
    interests = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    ratings = relationship("Rating", back_populates="user")
    enrollments = relationship("Enrollment", back_populates="user")

    @property
    def skills_list(self):
        return json.loads(self.skills) if self.skills else []
    @skills_list.setter
    def skills_list(self, value):
        self.skills = json.dumps(value)
    @property
    def interests_list(self):
        return json.loads(self.interests) if self.interests else []
    @interests_list.setter
    def interests_list(self, value):
        self.interests = json.dumps(value)


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    description = Column(Text, default="")
    skills_covered = Column(Text, default="[]")
    ratings = relationship("Rating", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

    @property
    def skills_list(self):
        return json.loads(self.skills_covered) if self.skills_covered else []


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="ratings")
    course = relationship("Course", back_populates="ratings")


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    page_progress = relationship("PageProgress", back_populates="enrollment", cascade="all, delete-orphan")


class PageProgress(Base):
    __tablename__ = "page_progress"
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    enrollment = relationship("Enrollment", back_populates="page_progress")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
