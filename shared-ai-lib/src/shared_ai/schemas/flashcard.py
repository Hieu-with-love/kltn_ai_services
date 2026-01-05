from pydantic import BaseModel
from typing import List

class Flashcard(BaseModel):
    question: str
    answer: str

class FlashcardResponse(BaseModel):
    status: str
    data: List[Flashcard]
    model: str
