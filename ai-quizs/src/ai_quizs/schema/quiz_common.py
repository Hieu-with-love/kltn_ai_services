from enum import Enum


class QuizType(str, Enum):
    SINGLE = "SINGLE_CHOICE"
    MULTIPLE = "MULTIPLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_IN_THE_BLANK"


class QuizDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
