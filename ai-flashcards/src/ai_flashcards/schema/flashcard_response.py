from pydantic import BaseModel
from ..utils.flashcard_common import DifficultyLevel

class Flashcard(BaseModel):
    front: str
    back: str
    tags: list[str]
    difficulty: DifficultyLevel = DifficultyLevel.EASY

class FlashCardResponse(BaseModel):
    cards: list[Flashcard]