from email import parser
from urllib import request
from urllib import request
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from shared_ai.llm.gemini import get_gemini_model

from ..schema.quiz_response import GenerateQuizResponse
from ..utils.quiz_utils import shuffle_quiz_options

def generate_quiz(topic: str, questions: list):
    """

    :param topic: str - The topic or content based on which the quiz is to be generated.
    :param questions: list - A list of question configurations specifying the types and formats of questions to be generated.
    :return: GenerateQuizResponse - The generated quiz in the form of a structured response, with options shuffled for each question.
    """

    llm = get_gemini_model(temperature=0.3) # trọng số thấp để giảm hallucination

    system_template = """
    You are an expert educational content generator.

    You MUST generate quiz questions strictly in valid JSON.
    The JSON MUST conform EXACTLY to the provided schema.
    DO NOT add explanations, markdown, or extra text.
    DO NOT change field names or enum values.
    If you are unsure, make a reasonable assumption but still follow the schema.

    Return ONLY valid JSON.
    """

    human_template = """
    Context:
    {content_or_topic}

    Question configuration:
    {question_config_json}

    Output JSON schema:
    {output_schema_json}
    """

    parser = PydanticOutputParser(
        pydantic_object=GenerateQuizResponse
    )

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = chat_prompt | llm | parser

    input_data = {
        "content_or_topic": topic,
        "question_config_json": questions,
        "output_schema_json": parser.get_format_instructions(),
    }

    raw_result = chain.invoke(input_data)
    
    return shuffle_quiz_options(raw_result)
    