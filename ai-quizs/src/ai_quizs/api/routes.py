from fastapi import APIRouter
from ..application.services import generate_quiz as generate_quiz_service
from ..schema.quiz_request import GenerateQuizRequest

router = APIRouter()

@router.post("/generate")
async def generate_quiz(request: GenerateQuizRequest):
    return generate_quiz_service(request.context, request.questions)
