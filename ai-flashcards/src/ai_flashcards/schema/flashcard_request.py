from pydantic import BaseModel, Field, field_validator, model_validator

from ..utils.flashcard_common import DifficultyLevel


class FlashcardNumberOfDifficultyConfig(BaseModel):
    difficulty: DifficultyLevel
    # Allow 0 so callers can pass an explicit "skip this level" entry (e.g. HARD=0)
    # while still rejecting negative numbers; the request-level validator below
    # guarantees the total is at least 1.
    numberOfCards: int = Field(ge=0)


class FlashCardRequest(BaseModel):
    internalDocument: str
    externalDocument: str | None = None
    cardsPerDifficulty: list[FlashcardNumberOfDifficultyConfig] = Field(min_length=1)
    language: str = "vietnamese"

    @field_validator("internalDocument")
    @classmethod
    def _internal_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("internalDocument must not be empty")
        return v

    @model_validator(mode="after")
    def _total_cards_positive(self) -> "FlashCardRequest":
        if sum(c.numberOfCards for c in self.cardsPerDifficulty) < 1:
            raise ValueError("cardsPerDifficulty must request at least 1 card in total")
        return self
