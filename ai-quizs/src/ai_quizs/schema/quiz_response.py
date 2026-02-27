from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Dict, Union, Literal, Annotated
from .quiz_common import QuizType, QuizDifficulty

class BaseQuestion(BaseModel):
    question: str
    
class UserOption(BaseModel):
    text: str
    is_correct: bool

class SingleChoiceQuestionResponse(BaseQuestion):
    question_type: Literal["SINGLE_CHOICE"] = QuizType.SINGLE.value
    options: List[UserOption] # Danh sách các lựa chọn và thông tin đúng/sai
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    # Validation đảm bảo chỉ có 4 lựa chọn, trong đó chỉ có 1 lựa chọn đúng
    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError('There must be exactly 4 options.')
        correct_answers = [opt for opt in v if opt.is_correct is True]
        if len(correct_answers) != 1:
            raise ValueError('There must be exactly one correct answer.')
        return v

class MultipleChoiceQuestionResponse(BaseQuestion):
    question_type: Literal["MULTIPLE_CHOICE"] = QuizType.MULTIPLE.value
    options: List[UserOption] # Danh sách các lựa chọn và thông tin đúng/sai
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    # Validation đảm bảo chỉ có 4 lựa chọn, trong đó có ít nhất 1 lựa chọn đúng
    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError('There must be exactly 4 options.')
        correct_answers = [opt for opt in v if opt.is_correct is True]
        if len(correct_answers) < 1:
            raise ValueError('There must be at least one correct answer.')
        return v

class TrueFalseQuestionResponse(BaseQuestion):
    question_type: Literal["TRUE_FALSE"] = QuizType.TRUE_FALSE.value
    options: List[UserOption] # Danh sách các lựa chọn và thông tin đúng/sai
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 2:
            raise ValueError('There must be exactly 2 options for True/False questions.')
        correct_answers = [opt for opt in v if opt.is_correct is True]
        if len(correct_answers) != 1:
            raise ValueError('There must be exactly one correct answer.')
        return v

class Blank(BaseModel):
    blank_number: int
    answer: str
class FillInTheBlankQuestionResponse(BaseQuestion):
    question_type: Literal["FILL_IN_THE_BLANK"] = QuizType.FILL_BLANK.value
    options: List[Blank] # Danh sách các đáp án đúng theo thứ tự blank: answers[0] cho [___1___], answers[1] cho [___2___], ...
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[int] = 1
    tags: Optional[List[str]] = []

    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) < 1:
            raise ValueError('Có ít nhất 1 chỗ trống trong câu hỏi điền vào chỗ trống.')
        return v

class GenerateQuizResponse(BaseModel):
    questions: List[
        Annotated[
            Union[
                SingleChoiceQuestionResponse,
                MultipleChoiceQuestionResponse,
                TrueFalseQuestionResponse,
                FillInTheBlankQuestionResponse
            ],
            Field(discriminator="question_type")
        ]
    ]