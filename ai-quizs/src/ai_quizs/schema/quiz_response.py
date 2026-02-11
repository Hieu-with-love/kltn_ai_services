from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Union
from .quiz_common import QuizType, QuizDifficulty

class BaseQuestion(BaseModel):
    question: str

class SingleChoiceQuestionResponse(BaseQuestion):
    options: List[Dict[str, bool]] # Danh sách các lựa chọn và thông tin đúng/sai
    question_type: str = QuizType.SINGLE.value
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    # Validation đảm bảo chỉ có 4 lựa chọn, trong đó chỉ có 1 lựa chọn đúng
    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError('There must be exactly 4 options.')
        correct_answers = [opt for opt in v if list(opt.values())[0] is True]
        if len(correct_answers) != 1:
            raise ValueError('There must be exactly one correct answer.')
        return v

class MultipleChoiceQuestionResponse(BaseQuestion):
    options: List[Dict[str, bool]] # Danh sách các lựa chọn và thông tin đúng/sai
    question_type: str = QuizType.MULTIPLE.value
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    # Validation đảm bảo chỉ có 4 lựa chọn, trong đó có ít nhất 1 lựa chọn đúng
    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError('There must be exactly 4 options.')
        correct_answers = [opt for opt in v if list(opt.values())[0] is True]
        if len(correct_answers) < 1:
            raise ValueError('There must be at least one correct answer.')
        return v

class TrueFalseOption(BaseModel):
    text: str
    is_correct: bool

class TrueFalseQuestionResponse(BaseQuestion):
    options: List[TrueFalseOption] # Danh sách các lựa chọn và thông tin đúng/sai
    question_type: str = QuizType.TRUE_FALSE.value
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 2:
            raise ValueError('There must be exactly 2 options for True/False questions.')
        correct_answers = [opt for opt in v if list(opt.values())[0] is True]
        if len(correct_answers) != 1:
            raise ValueError('There must be exactly one correct answer.')
        return v

class FillInTheBlankQuestionResponse(BaseQuestion):
    answer: List[str] # Danh sách các câu trả lời đúng
    question_type: str = QuizType.FILL_BLANK.value
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    @field_validator('answer')
    @classmethod
    def validate_answer(cls, v):
        if len(v) < 1:
            raise ValueError('There must be at least one correct answer.')
        return v

class GenerateQuizResponse(BaseModel):
    questions: List[
        Union[
            SingleChoiceQuestionResponse,
            MultipleChoiceQuestionResponse,
            TrueFalseQuestionResponse,
            FillInTheBlankQuestionResponse
        ]
    ]