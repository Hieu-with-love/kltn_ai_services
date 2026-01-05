from pydantic import BaseModel
from typing import List

class FlashcardRequest(BaseModel):
    courseId: str
    lessonId: str
    content: str
    numberOfCards: int
    language: str = "vi"
