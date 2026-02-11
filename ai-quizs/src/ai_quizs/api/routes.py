from fastapi import APIRouter
from ..application.services import generate_quiz as generate_quiz_service
from ..schema.quiz_request import GenerateQuizRequestByTopic

router = APIRouter()

@router.post("/generate")
async def generate_quiz(request: GenerateQuizRequestByTopic):
    return generate_quiz_service(request.topic, request.questions)