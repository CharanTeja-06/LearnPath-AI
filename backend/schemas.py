"""
Pydantic schemas for request / response validation.
"""

from pydantic import BaseModel
from typing import List, Optional


class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    skills: List[str] = []
    interests: List[str] = []

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    skills: List[str]
    interests: List[str]
    class Config:
        from_attributes = True

class CourseResponse(BaseModel):
    id: int
    name: str
    category: str
    difficulty: str
    description: str
    skills_covered: List[str]
    avg_rating: Optional[float] = None

class RateCourseRequest(BaseModel):
    course_id: int
    rating: float

class RecommendationItem(BaseModel):
    course_id: int
    course_name: str
    category: str
    difficulty: str
    predicted_score: float
    explanation: str

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
    model_info: dict

class EnrollRequest(BaseModel):
    course_id: int

class PageCompleteRequest(BaseModel):
    course_id: int
    page_number: int

class PageInfo(BaseModel):
    page_number: int
    title: str
    completed: bool

class EnrollmentInfo(BaseModel):
    enrollment_id: int
    course_id: int
    course_name: str
    category: str
    difficulty: str
    total_pages: int
    completed_pages: int
    progress_percent: float
