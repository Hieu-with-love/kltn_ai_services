from fastapi import APIRouter, HTTPException
from ..application.services import generate_quiz_async
from ..schema.quiz_request import GenerateQuizRequest
from ..schema.quiz_response import GenerateQuizResponse
from ..schema.api_response import ApiResponse, ErrorDetail

router = APIRouter()


def _err(code: str, message: str) -> ApiResponse:
    return ApiResponse(
        success=False,
        data=None,
        error=ErrorDetail(code=code, message=message, partial_results=None),
    )


@router.post("/generate", response_model=ApiResponse[GenerateQuizResponse])
async def generate_questions(request: GenerateQuizRequest):
    """
    Generate quiz endpoint với parallel processing cho 2 nhóm câu hỏi.

    NHÓM 1: SINGLE_CHOICE, MULTIPLE_CHOICE, TRUE_FALSE
    NHÓM 2: FILL_IN_THE_BLANK
    """
    total = sum(c.number for q in request.questions for c in q.numberOfQuestions)
    if total <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total numberOfQuestions must be greater than 0",
        )

    try:
        result = await generate_quiz_async(
            context=request.context,
            questions=request.questions,
            language=(request.language or "vietnamese"),
        )
        return ApiResponse(success=True, data=result, error=None)
    except Exception as e:
        return _err("AI_GENERATION_FAILED", str(e))
