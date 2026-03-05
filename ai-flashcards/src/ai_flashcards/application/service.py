from ai_flashcards.domain.flashcard_generator import generate_flashcards

class FlashcardService:
    def generate(self, req):
        # Pass API request directly to domain
        result = generate_flashcards(req)
        return result
