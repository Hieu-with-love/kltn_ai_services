from ai_flashcards.domain.flashcard_generator import generate_flashcards

class FlashcardService:
    def generate(self, req):
        cards = generate_flashcards(
            content=req.content,
            n=req.numberOfCards,
            language=req.language
        )

        return {
            "status": "SUCCESS",
            "data": cards,
            "model": "gemini-2.5-flash"
        }
