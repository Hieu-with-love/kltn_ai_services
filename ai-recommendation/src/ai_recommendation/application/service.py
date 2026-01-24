from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from shared_ai.llm.gemini import get_gemini_model
from ai_recommendation.api.schemas import RecommendationRequest, RecommendationResponse
import json

class RecommendationService:
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.1)

    async def recommend(self, req: RecommendationRequest) -> RecommendationResponse:
        # Format candidates for the prompt
        candidates_text = "\n".join([f"- ID: {c.id} | Title: {c.title} | Desc: {c.description}" for c in req.candidates])
        
        parser = JsonOutputParser()
        
        prompt = ChatPromptTemplate.from_template("""
        Bạn là một chuyên gia tư vấn giáo dục AI.
        Nhiệm vụ: Sắp xếp lại danh sách khóa học (Candidates) dựa trên Hồ sơ người dùng (User Profile) để tìm ra những khóa học phù hợp nhất.

        Thông tin người dùng:
        - Sở thích: {interests}
        - Lịch sử đã học: {history}

        Danh sách khóa học ứng viên:
        {candidates}

        Yêu cầu:
        1. Phân tích sở thích và lộ trình học tập của người học.
        2. Chọn ra {top_k} khóa học phù hợp nhất.
        3. Ưu tiên các khóa học nâng cao hoặc bổ trợ cho lịch sử đã học (Progression).
        4. Trả về kết quả dưới dạng JSON thuần túy theo cấu trúc:
        {{
            "ranked_ids": ["id1", "id2", ...],
            "reasoning": "Giải thích ngắn gọn tại sao chọn thứ tự này..."
        }}
        
        {format_instructions}
        """)

        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "interests": ", ".join(req.user_profile.interests),
                "history": ", ".join(req.user_profile.history),
                "candidates": candidates_text,
                "top_k": req.top_k,
                "format_instructions": parser.get_format_instructions()
            })
            
            ranked_ids = result.get("ranked_ids", [])
            reasoning = result.get("reasoning", "")
            
            # Re-order the candidate objects based on IDs
            candidate_map = {c.id: c for c in req.candidates}
            ordered_candidates = []
            for cid in ranked_ids:
                if cid in candidate_map:
                    ordered_candidates.append(candidate_map[cid])
            
            # If AI returned fewer items than top_k, we might want to fill the rest or just return what we have.
            # Here we strictly return what AI picked.
            
            return RecommendationResponse(
                recommendations=ordered_candidates,
                reasoning=reasoning
            )

        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Fallback: Return original order
            return RecommendationResponse(
                recommendations=req.candidates[:req.top_k],
                reasoning=f"Error in AI processing: {str(e)}. Returning default order."
            )
