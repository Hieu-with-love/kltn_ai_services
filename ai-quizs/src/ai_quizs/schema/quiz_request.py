from pydantic import BaseModel
from typing import List, Optional
from .quiz_common import QuizType, QuizDifficulty


class QuestionTypeConfig(BaseModel):
    difficulty: Optional[QuizDifficulty] = QuizDifficulty.EASY
    number: int


class QuizQuestionConfig(BaseModel):
    type: QuizType
    numberOfQuestions: List[QuestionTypeConfig]


class GenerateQuizRequest(BaseModel):
    context: str
    questions: List[QuizQuestionConfig]
    language: Optional[str] = "vietnamese"
