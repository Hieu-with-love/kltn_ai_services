from pydantic import BaseModel
from typing import List

class QuizTopicRequest(BaseModel):
    topic: str
    num_questions: int

class QuizRequest(BaseModel):
    topic: str
    num_questions: int
    content: str
    difficulty: str

class QuizResponse(BaseModel):
    questions: List[str]
    answers: List[str]
