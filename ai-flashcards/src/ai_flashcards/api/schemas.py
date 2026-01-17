from pydantic import BaseModel
from typing import List

class CourseFlashcardRequest(BaseModel):
    courseId: str
    lessonId: str

    # Nội dung lấy từ lesson
    content: str | None = None

    # Nội dung trích xuất từ file
    extractedContent: str | None = None

    numberOfCards: int
    language: str = "vi"

class FlashCardRequest(BaseModel):
    content: str | None = None
    extractedContent: str | None = None
    numberOfCards: int

class FlashCard(BaseModel):
    front: str
    back: str

class FlashCardResponse(BaseModel):
    status: str
    data: List[FlashCard]