from email import parser
from urllib import request
from urllib import request
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from shared_ai.llm.gemini import get_gemini_model

from ..schema.quiz_response import GenerateQuizResponse
from ..utils.quiz_utils import shuffle_quiz_options

def generate_quiz(context: str, questions: list, language: str = "Vietnamese"):
    """

    Tạo quiz dựa trên nội dung và với số lượng và loại câu hỏi được chỉ định.
    Sử dụng Gemini LLM để tạo quiz, với trọng số thấp để giảm hallucination và đảm bảo tính chính xác của câu hỏi.
    Đảo lộn thứ tự đáp án của mỗi câu hỏi trong quiz để đảm bảo tính ngẫu nhiên và tránh việc người dùng có thể đoán được đáp án dựa trên vị trí.

    :param context: str - The context or content based on which the quiz is to be generated.
    :param questions: list - A list of question configurations specifying the types and formats of questions to be generated.
    :param language: str - The language in which the quiz should be generated.
    :return: GenerateQuizResponse - The generated quiz in the form of a structured response, with options shuffled for each question.
    """

    llm = get_gemini_model(temperature=0.3) # trọng số thấp để giảm hallucination

    system_template = """
        You are an expert educational content generator.

        STRICT OUTPUT REQUIREMENTS:
        - Output MUST be valid JSON.
        - MUST strictly follow the provided schema.
        - DO NOT add explanations, comments, or markdown.
        - DO NOT change field names or enum values.
        - DO NOT include text outside the JSON.
        - Provide tag based on question topics for categorization lowercase and without special characters
            (e.g., "oop", "data structures", "algorithms", "python", etc.) in the "tags" field.

        LANGUAGE REQUIREMENT:
        - All questions, options, and explanations (if any) must be written in the specified language.

        STRUCTURAL RULES BY QUESTION TYPE:

        SINGLE_CHOICE:
        - Exactly 4 options.
        - Exactly 1 correct option.

        MULTIPLE_CHOICE:
        - Exactly 4 options.
        - At least 1 correct option.

        TRUE_FALSE:
        - Exactly 2 options.
        - Exactly 1 correct option.

        FILL_IN_THE_BLANK:
        - The question may contain one or more blanks.
            + For EASY difficulty: 2 blanks.
            + For MEDIUM difficulty: 3 blanks.
            + For HARD difficulty: 4 blanks.
        - Replace each blank with numbered format [___1___], [___2___], [___3___], etc.
        - MUST include "answers" field as an array of strings (REQUIRED, NOT NULL).
        - The "answers" array contains correct answers in order: answers[0] for [___1___], answers[1] for [___2___], etc.
        - Only include correct answers as plain strings, NO distractors needed.
        - Example: "answers": ["encapsulation", "private", "getter"]

        Return ONLY valid JSON.
    """

    human_template = """
    Context:
    {content_or_topic}

    Question configuration:
    {question_config_json}
    
    Language: {language}

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
        "content_or_topic": context,
        "question_config_json": questions,
        "language": language,
        "output_schema_json": parser.get_format_instructions(),
    }
    questions_result = chain.invoke(input_data)
    
    return shuffle_quiz_options(questions_result)
    