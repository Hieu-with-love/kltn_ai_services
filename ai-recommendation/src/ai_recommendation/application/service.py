from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from shared_ai.llm.gemini import get_gemini_model
from ai_recommendation.api.schemas import RecommendationRequest, RecommendationResponse
import logging
import re
import math
import json

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.llm = get_gemini_model(temperature=0.1)

    async def recommend(self, req: RecommendationRequest) -> RecommendationResponse:
        ranked_candidates, score_breakdowns = self._rank_candidates(req)
        self._log_score_breakdown(score_breakdowns, limit=min(req.top_k, 5))
        # Format candidates for the prompt in a hybrid-ranked order
        candidates_text = "\n".join(
            [f"- ID: {c.id} | Title: {c.title} | Desc: {c.description}" for c in ranked_candidates]
        )

        parser = JsonOutputParser()
        
        # Enhanced prompt with behavioral signals
        prompt = ChatPromptTemplate.from_template("""
        Bạn là một chuyên gia tư vấn giáo dục AI với kỹ năng phân tích hành vi học tập.
        Nhiệm vụ: Sắp xếp lại danh sách khóa học (Candidates) dựa trên Hồ sơ người dùng (User Profile) để tìm ra những khóa học phù hợp nhất.

        ═══════════════════════════════════════════════════════════════
        THÔNG TIN NGƯỜI DÙNG:
        ═══════════════════════════════════════════════════════════════
        
        SỞ THÍCH (Interests) - Derived from:
          • Courses user favorited (explicit preference)
          • Courses with high engagement (>50% progress) - strong signal!
          • Courses user reviewed - indicates strong opinion/satisfaction
        Danh sách: {interests}

        LỊCH SỬ ĐÃ HỌC (Learning History) - From:
          • Courses user purchased/completed
          • Indicates successful learning path & readiness for progression
        Danh sách: {history}

        TÍN HIỆU HÀNH VI (Behavior Signals) - From:
          • Page visits / clicks on course pages
          • Quiz attempts and average scores
          • Engagement hints derived from activity patterns
        Danh sách: {behavior_signals}

        TÍN HIỆU COLLABORATIVE (Collaborative Signals) - From:
          • Users similar to this learner liked these courses
          • Courses frequently co-favorited or co-purchased
          • Item-item similarity from real user actions
        Danh sách: {collaborative_signals}

        ═══════════════════════════════════════════════════════════════
        DANH SÁCH KHÓA HỌC ĐƯỢC ĐỀ XUẤT:
        ═══════════════════════════════════════════════════════════════
        {candidates}

        ═══════════════════════════════════════════════════════════════
        HƯỚNG DẪN XẾPHẠNG:
        ═══════════════════════════════════════════════════════════════
        
        1. PHÂN TÍCH NGƯỜI DÙNG:
           - Xác định lĩnh vực chính quan tâm từ sở thích
           - Đánh giá level hiện tại từ lịch sử học tập
           - Xác định lộ trình tiếp theo (progression)

        2. XẾPHẠNG THÔNG MINH:
           ✓ ƯU TIÊN HÀNG ĐẦU (Score: 9-10):
             • Bổ sung kỹ năng cho courses đã học (progression)
             • Liên quan trực tiếp đến sở thích hàng đầu
             • Đúng level: không quá dễ, không quá khó
             
           ✓ HÀNG ĐỎI (Score: 7-8):
             • Nâng rộng kiến thức trong lĩnh vực quan tâm
             • Complementary skills cho lĩnh vực chính
             
           ✓ HÀNG BA (Score: 5-6):
             • Cross-domain learning (từ sở thích liên quan)

        3. LOẠI BỎ:
           - Courses ngoài sở thích của user
           - Courses user đã mua (đã filtered từ backend)
           - Courses quá cơ bản/nâng cao so với level hiện tại

        4. DIVERSITY:
           - Không tất cả cùng 1 lĩnh vực
           - Mix: core skill + soft skill + complementary

        ═══════════════════════════════════════════════════════════════
        OUTPUT FORMAT (JSON ONLY):
        ═══════════════════════════════════════════════════════════════
        {{
            "ranked_ids": ["id1", "id2", "id3", ...],
            "reasoning": "Giải thích chi tiết: Tại sao chọn thứ tự này? Người dùng có sở thích X, đã học Y, nên tiếp theo nên học Z..."
        }}
        
        {format_instructions}
        """)

        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "interests": ", ".join(req.user_profile.interests) if req.user_profile.interests else "No data",
                "history": ", ".join(req.user_profile.history) if req.user_profile.history else "New user",
                "behavior_signals": ", ".join(req.user_profile.behavior_signals) if getattr(req.user_profile, "behavior_signals", None) else "No behavior signals",
                "collaborative_signals": ", ".join(req.user_profile.collaborative_signals) if getattr(req.user_profile, "collaborative_signals", None) else "No collaborative signals",
                "candidates": candidates_text,
                "top_k": req.top_k,
                "format_instructions": parser.get_format_instructions()
            })
            
            ranked_ids = result.get("ranked_ids", [])
            reasoning = result.get("reasoning", "")
            
            # Re-order the candidate objects based on IDs
            candidate_map = {c.id: c for c in ranked_candidates}
            ordered_candidates = []
            for cid in ranked_ids:
                if cid in candidate_map:
                    ordered_candidates.append(candidate_map[cid])

            # If LLM returns fewer IDs, fill remaining slots with deterministic pre-ranked candidates.
            if len(ordered_candidates) < req.top_k:
                existing_ids = {c.id for c in ordered_candidates}
                for candidate in ranked_candidates:
                    if candidate.id not in existing_ids:
                        ordered_candidates.append(candidate)
                        existing_ids.add(candidate.id)
                    if len(ordered_candidates) >= req.top_k:
                        break
            
            # Ensure we return exactly top_k items
            ordered_candidates = ordered_candidates[:req.top_k]
            
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

    def _rank_candidates(self, req: RecommendationRequest):
        interest_tokens = self._build_tokens(req.user_profile.interests)
        behavior_tokens = self._build_tokens(getattr(req.user_profile, "behavior_signals", []))
        collaborative_tokens = self._build_tokens(getattr(req.user_profile, "collaborative_signals", []))
        history_weighted_tokens = self._build_weighted_tokens(req.user_profile.history)

        anchor_texts = [
            *(req.user_profile.interests or []),
            *(req.user_profile.history or []),
        ]

        behavior_boost = self._extract_signal_boost_map(getattr(req.user_profile, "behavior_signals", []))
        collaborative_boost = self._extract_signal_boost_map(getattr(req.user_profile, "collaborative_signals", []))

        scored_candidates = []
        breakdowns = []
        for candidate in req.candidates:
            candidate_text = f"{candidate.title} {candidate.description}"
            candidate_tokens = self._build_tokens([candidate_text])
            similarity_score = self._max_similarity_to_anchors(candidate_text, anchor_texts)
            recency_score = self._weighted_overlap(candidate_tokens, history_weighted_tokens)

            title_key = (candidate.title or "").strip().lower()
            trend_score = behavior_boost.get(title_key, 0.0) + collaborative_boost.get(title_key, 0.0)

            collaborative_component = 3.0 * self._token_overlap(candidate_tokens, collaborative_tokens)
            interest_component = 2.0 * self._token_overlap(candidate_tokens, interest_tokens)
            behavior_component = 1.0 * self._token_overlap(candidate_tokens, behavior_tokens)
            similarity_component = 4.0 * similarity_score
            recency_component = 2.0 * recency_score

            score = (
                collaborative_component
                + interest_component
                + behavior_component
                + similarity_component
                + recency_component
                + trend_score
            )

            scored_candidates.append((score, candidate))
            breakdowns.append({
                "candidate_id": candidate.id,
                "title": candidate.title,
                "total": score,
                "collaborative": collaborative_component,
                "interest": interest_component,
                "behavior": behavior_component,
                "similarity": similarity_component,
                "recency": recency_component,
                "trend": trend_score,
            })

        scored_candidates.sort(key=lambda item: (-item[0], item[1].title.lower(), item[1].id))
        breakdowns.sort(key=lambda item: -item["total"])
        return [candidate for _, candidate in scored_candidates], breakdowns

    def _log_score_breakdown(self, breakdowns, limit=5):
        for item in (breakdowns or [])[:limit]:
            logger.info(
                "HybridScore course='%s' id=%s total=%.3f [collab=%.3f interest=%.3f behavior=%.3f sim=%.3f recency=%.3f trend=%.3f]",
                item["title"],
                item["candidate_id"],
                item["total"],
                item["collaborative"],
                item["interest"],
                item["behavior"],
                item["similarity"],
                item["recency"],
                item["trend"],
            )

    def _build_tokens(self, values):
        tokens = set()
        for value in values or []:
            for token in re.findall(r"[a-z0-9]+", str(value).lower()):
                if len(token) > 2:
                    tokens.add(token)
        return tokens

    def _build_weighted_tokens(self, values):
        weighted_tokens = {}
        for index, value in enumerate(values or []):
            # Time-decay: more recent history entries carry higher weight.
            decay = math.exp(-0.35 * index)
            for token in re.findall(r"[a-z0-9]+", str(value).lower()):
                if len(token) > 2:
                    weighted_tokens[token] = max(weighted_tokens.get(token, 0.0), decay)
        return weighted_tokens

    def _weighted_overlap(self, candidate_tokens, weighted_tokens):
        if not candidate_tokens or not weighted_tokens:
            return 0.0
        return sum(weighted_tokens.get(token, 0.0) for token in candidate_tokens)

    def _text_similarity(self, left_text, right_text):
        left_tokens = self._build_tokens([left_text])
        right_tokens = self._build_tokens([right_text])
        if not left_tokens or not right_tokens:
            return 0.0
        intersection = len(left_tokens.intersection(right_tokens))
        union = len(left_tokens.union(right_tokens))
        if union == 0:
            return 0.0
        return intersection / union

    def _max_similarity_to_anchors(self, candidate_text, anchors):
        if not anchors:
            return 0.0
        return max(self._text_similarity(candidate_text, anchor_text) for anchor_text in anchors)

    def _extract_signal_boost_map(self, signals):
        boosts = {}
        for signal in signals or []:
            text = str(signal)
            title_match = re.search(r"'([^']+)'", text)
            if not title_match:
                continue

            title = title_match.group(1).strip().lower()
            nums = [float(num) for num in re.findall(r"\d+(?:\.\d+)?", text)]
            if not nums:
                continue

            raw = max(nums)
            # Compress large counts/scores into a small stable range.
            boosts[title] = boosts.get(title, 0.0) + min(math.log1p(raw), 3.0)
        return boosts

    def _token_overlap(self, left_tokens, right_tokens):
        if not left_tokens or not right_tokens:
            return 0
        return len(left_tokens.intersection(right_tokens))
