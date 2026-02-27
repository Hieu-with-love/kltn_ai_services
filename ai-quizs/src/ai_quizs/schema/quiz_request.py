from pydantic import BaseModel
from typing import List, Optional
from .quiz_common import QuizType, QuizDifficulty

class QuizNumberConfig(BaseModel):
    difficulty: Optional[QuizDifficulty] = QuizDifficulty.EASY
    number: int

class QuizTypeConfig(BaseModel):
    type: QuizType
    numberOfQuestions: List[QuizNumberConfig]

class GenerateQuizRequest(BaseModel):
    context: str # Chủ đề do Teacher cung cấp or Nội dung đã extract + summary (Teacher có thể sửa)
    questions: List[QuizTypeConfig] # Loại câu hỏi và số lượng câu hỏi cho mỗi loại