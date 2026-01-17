# src/ai_flashcards/api/routes.py
from fastapi import APIRouter
from ai_flashcards.api.schemas import FlashCardRequest
from ai_flashcards.application.service import FlashcardService

router = APIRouter()

@router.post("/generate")
def generate_flashcards(req: FlashCardRequest):
    return FlashcardService().generate(req)

@router.post("/generate/course/{course_id}/lesson/{lesson_id}")
def generate_flashcards_from_course_lesson(course_id: str, lesson_id: str):
    # Placeholder for future implementation
    pass
