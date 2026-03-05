from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from shared_ai.llm.gemini import get_gemini_model
from typing import List
from ..utils.flashcard_common import DifficultyLevel
from ..schema.flashcard_request import FlashCardRequest
from ..schema.flashcard_response import FlashCardResponse

def generate_flashcards(request: FlashCardRequest):
    
    """
    
    """
    
    # 1. Define the llm. Upgrade temperature to reduce halucination.
    llm = get_gemini_model(temperature=0.7)
    
    # 2. Define the prompt template, pass to some parameters to make it more dynamic
    system_template = """
    You are a helpful assistant for generating flashcards to help students review knowledge.
    
    Your task is to create flashcards based on the provided documents. Each flashcard should have:
    - front: A clear question or prompt
    - back: A concise and accurate answer
    - tags: Relevant keywords or topics (2-5 tags per card)
    - difficulty: EASY, MEDIUM, or HARD
    
    Guidelines:
    - Focus primarily on the internal document content, which contains the core material
    - If external document is provided, use it as supplementary context or to add examples
    - Ensure questions are clear, specific, and test understanding
    - Answers should be concise but complete
    - Vary question types (definitions, explanations, applications, comparisons)
    - Distribute cards across the requested difficulty levels appropriately
    
    {format_instructions}
    """
    
    human_template = """
    Generate flashcards in {language} based on the following:
    
    INTERNAL DOCUMENT (Primary Source):
    {internalDocument}
    
    {external_section}
    
    Requirements:
    {cards_requirements}
    
    Generate the flashcards now, ensuring they follow the specified format exactly.
    """
    
    output_parser = PydanticOutputParser(pydantic_object=FlashCardResponse)
    
    # Prepare external document section
    external_section = ""
    if request.externalDocument:
        external_section = f"EXTERNAL DOCUMENT (Supplementary):\n{request.externalDocument}"
    else:
        external_section = "No external document provided."
    
    # Prepare cards requirements
    cards_requirements = "\n".join([
        f"- {config.numberOfCards} cards at {config.difficulty} difficulty level"
        for config in request.cardsPerDifficulty
    ])
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_message_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # 3. Define pipeline to generate flashcards
    chain = chat_message_prompt | llm | output_parser
    
    input_data = {
        "internalDocument": request.internalDocument,
        "external_section": external_section,
        "cards_requirements": cards_requirements,
        "language": request.language,
        "format_instructions": output_parser.get_format_instructions()
    }
    
    cards_response = chain.invoke(input_data)
    return cards_response.dict()