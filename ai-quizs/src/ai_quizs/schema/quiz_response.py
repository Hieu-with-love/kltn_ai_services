from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Union, Literal, Annotated
from .quiz_common import QuizType, QuizDifficulty


class ChoiceOption(BaseModel):
    text: str
    is_correct: bool


class BlankOption(BaseModel):
    blank_number: int
    answer: str


class BaseQuestion(BaseModel):
    question: str
    difficulty: Optional[str] = QuizDifficulty.EASY.value
    score: Optional[float] = 1
    tags: List[str] = Field(default_factory=list)
    options: List[ChoiceOption] = Field(default_factory=list)
    answers: List[BlankOption] = Field(default_factory=list)


class SingleChoiceQuestion(BaseQuestion):
    question_type: Literal["SINGLE_CHOICE"] = QuizType.SINGLE.value

    @field_validator("options")
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError("There must be exactly 4 options.")
        correct = [opt for opt in v if opt.is_correct is True]
        if len(correct) != 1:
            raise ValueError("There must be exactly one correct answer.")
        return v


class MultipleChoiceQuestion(BaseQuestion):
    question_type: Literal["MULTIPLE_CHOICE"] = QuizType.MULTIPLE.value

    @field_validator("options")
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError("There must be exactly 4 options.")
        correct = [opt for opt in v if opt.is_correct is True]
        if len(correct) < 1:
            raise ValueError("There must be at least one correct answer.")
        return v


class TrueFalseQuestion(BaseQuestion):
    question_type: Literal["TRUE_FALSE"] = QuizType.TRUE_FALSE.value

    @field_validator("options")
    @classmethod
    def validate_options(cls, v):
        if len(v) != 2:
            raise ValueError("There must be exactly 2 options for True/False questions.")
        correct = [opt for opt in v if opt.is_correct is True]
        if len(correct) != 1:
            raise ValueError("There must be exactly one correct answer.")
        return v


class FillInTheBlankQuestion(BaseQuestion):
    question_type: Literal["FILL_IN_THE_BLANK"] = QuizType.FILL_BLANK.value

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v):
        if len(v) < 1:
            raise ValueError("Có ít nhất 1 chỗ trống trong câu hỏi điền vào chỗ trống.")
        return v


class GenerateQuizResponse(BaseModel):
    questions: List[
        Annotated[
            Union[
                SingleChoiceQuestion,
                MultipleChoiceQuestion,
                TrueFalseQuestion,
                FillInTheBlankQuestion,
            ],
            Field(discriminator="question_type"),
        ]
    ]
