from ai_flashcards.domain.flashcard_generator import generate_flashcards

class FlashcardService:
    def generate(self, req):
        text = ""

        if req.content:
            text += req.content + "\n"

        if req.extractedContent:
            text += req.extractedContent + "\n"

        cards = generate_flashcards(
            content=text,
            n=req.numberOfCards,
        )

        return {
            "status": "SUCCESS",
            "data": cards,
            "model": "gemini-2.5-flash"
        }

    # def generate_from_course_lesson(self, req):

    #     return self.generate(req)
