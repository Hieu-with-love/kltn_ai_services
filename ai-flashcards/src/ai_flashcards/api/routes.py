# src/ai_flashcards/api/routes.py
from fastapi import APIRouter
from ai_flashcards.api.schemas import FlashcardRequest
from ai_flashcards.application.service import FlashcardService

router = APIRouter()

@router.post("/generate")
def generate_flashcards(req: FlashcardRequest):
    return FlashcardService().generate(req)
