# src/ai_flashcards/api/routes.py
from fastapi import APIRouter, HTTPException

from ai_flashcards.application.service import FlashcardService

from ..schema.flashcard_request import FlashCardRequest
from ..schema.flashcard_response import FlashCardResponse

router = APIRouter()


@router.post("/generate", response_model=FlashCardResponse)
def generate_flashcards(req: FlashCardRequest):
    return FlashcardService().generate(req)


@router.post("/generate/course/{course_id}/lesson/{lesson_id}")
def generate_flashcards_from_course_lesson(course_id: str, lesson_id: str):
    """Generate flashcards for a specific lesson within a course.

    TODO: Lấy nội dung lesson từ course-service, tự build internalDocument
    từ lesson content (đặt mỗi CĐR trong block `=== Tên CĐR ===`), rồi gọi
    FlashcardService().generate(...) với một cardsPerDifficulty mặc định.
    Ở pass này chưa tích hợp course-service nên trả về 501.
    """
    raise HTTPException(status_code=501, detail="Endpoint not implemented yet")
