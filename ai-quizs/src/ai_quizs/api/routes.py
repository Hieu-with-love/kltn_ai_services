from fastapi import APIRouter, HTTPException
from ..application.services import generate_quiz_async
from ..schema.quiz_request import GenerateQuizRequest
from ..schema.quiz_response import GenerateQuizResponse
from ..schema.api_response import ApiResponse, ErrorDetail

router = APIRouter()

@router.post("/generate", response_model=ApiResponse[GenerateQuizResponse])
async def generate_questions(request: GenerateQuizRequest):
    """
    Generate quiz endpoint với parallel processing cho 2 nhóm câu hỏi.
    
    NHÓM 1: SINGLE_CHOICE, MULTIPLE_CHOICE, TRUE_FALSE
    NHÓM 2: FILL_IN_THE_BLANK
    
    Returns standardized API response với success status và data/error.
    
    :param request: GenerateQuizRequest - Request body chứa context và question configs
    :return: ApiResponse[GenerateQuizResponse] - Standardized response envelope
    """
    try:
        result = await generate_quiz_async(
            context=request.context,
            questions=request.questions,
            language="Vietnamese"  # Default language
        )
        return ApiResponse(success=True, data=result, error=None)
    except Exception as e:
        # Return error trong response envelope thay vì raise HTTPException
        # Điều này giúp Java service dễ dàng parse response
        return ApiResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code="AI_GENERATION_FAILED",
                message=str(e),
                partial_results=None
            )
        )
