from pydantic import BaseModel
from ..utils.flashcard_common import DifficultyLevel

class FlashcardNumberOfDifficultyConfig(BaseModel):
    difficulty: DifficultyLevel
    numberOfCards: int

class FlashCardRequest(BaseModel):
    internalDocument: str
    externalDocument: str | None = None
    cardsPerDifficulty: list[FlashcardNumberOfDifficultyConfig]
    language: str = "vietnamese"