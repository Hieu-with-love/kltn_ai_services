from fastapi import APIRouter, Depends
from ai_recommendation.api.schemas import RecommendationRequest, RecommendationResponse
from ai_recommendation.application.service import RecommendationService

router = APIRouter()

def get_service():
    return RecommendationService()

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_courses(
    req: RecommendationRequest,
    service: RecommendationService = Depends(get_service)
):
    print(f"--- [RECV] Full Request Payload: {req.model_dump()} ---")
    print(f"--- [RECV] Request from User: {req.user_profile.user_id} ---")
    print(f"Interests: {req.user_profile.interests}")
    
    response = await service.recommend(req)
    
    print(f"--- [SEND] AI Recommendation Result ---")
    print(f"Reasoning: {response.reasoning}")
    print(f"Top 3 Recommended IDs: {[c.id for c in response.recommendations[:3]]}")
    print("---------------------------------------")
    
    return response
