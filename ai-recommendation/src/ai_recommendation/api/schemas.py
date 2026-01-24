from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfile(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    interests: List[str] = Field(..., description="List of user interests or tags, e.g., ['Web Dev', 'React']")
    history: List[str] = Field(..., description="List of course titles/descriptions the user has completed or viewed")

class CourseCandidate(BaseModel):
    id: str = Field(..., description="Unique course ID")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Short description or summary of the course")

class RecommendationRequest(BaseModel):
    user_profile: UserProfile
    candidates: List[CourseCandidate]
    top_k: int = Field(5, description="Number of recommendations to return")

class RecommendationResponse(BaseModel):
    recommendations: List[CourseCandidate]
    reasoning: Optional[str] = Field(None, description="Explanation from AI about the ranking")
