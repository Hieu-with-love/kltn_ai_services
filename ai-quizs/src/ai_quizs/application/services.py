import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Annotated, Union
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from shared_ai.llm.gemini import get_gemini_model

from ..schema.quiz_response import (
    GenerateQuizResponse, 
    SingleChoiceQuestion, 
    MultipleChoiceQuestion, 
    TrueFalseQuestion,
    FillInTheBlankQuestion
)
from ..utils.quiz_utils import shuffle_quiz_options_all

def _generate_choice_questions(context: str, questions: list, language: str = "Vietnamese") -> GenerateQuizResponse:
    """
    Xử lý NHÓM 1: SINGLE_CHOICE, MULTIPLE_CHOICE, TRUE_FALSE
    Schema đồng nhất với ChoiceOption (text, is_correct)
    
    :param context: str - The context or content based on which the quiz is to be generated.
    :param questions: list - A list of question configurations for choice-based questions.
    :param language: str - The language in which the quiz should be generated.
    :return: GenerateQuizResponse - The generated quiz with choice-based questions.
    """
    
    # Response schema cho nhóm choice questions
    class ChoiceQuizResponse(BaseModel):
        questions: List[
            Annotated[
                Union[SingleChoiceQuestion, MultipleChoiceQuestion, TrueFalseQuestion],
                Field(discriminator="question_type")
            ]
        ]
    
    llm = get_gemini_model(temperature=0.3)  # Trọng số thấp để giảm hallucination

    system_template = """
        You are an expert educational content generator specializing in CHOICE-BASED QUESTIONS.

        STRICT OUTPUT REQUIREMENTS:
        - Output MUST be valid JSON.
        - MUST strictly follow the provided schema.
        - DO NOT add explanations, comments, or markdown.
        - DO NOT change field names or enum values.
        - DO NOT include text outside the JSON.
        - Provide tags based on question topics for categorization lowercase and without special characters
            (e.g., "oop", "data structures", "algorithms", "python", etc.) in the "tags" field.

        LANGUAGE REQUIREMENT:
        - All questions, options, and explanations (if any) must be written in the specified language.

        STRUCTURAL RULES BY QUESTION TYPE:

        SINGLE_CHOICE:
        - Exactly 4 options with "text" and "is_correct" fields.
        - Exactly 1 correct option (is_correct = true).
        - Ensure distractors are plausible but clearly incorrect.

        MULTIPLE_CHOICE:
        - Exactly 4 options with "text" and "is_correct" fields.
        - At least 1 correct option (is_correct = true).
        - Can have 2-3 correct answers for medium/hard difficulty.

        TRUE_FALSE:
        - Exactly 2 options with "text" and "is_correct" fields.
        - One option is "True" or equivalent, the other is "False" or equivalent.
        - Exactly 1 correct option.

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

    parser = PydanticOutputParser(pydantic_object=ChoiceQuizResponse)

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
    result = chain.invoke(input_data)
    
    return GenerateQuizResponse(questions=result.questions)


def _generate_fill_blank_questions(context: str, questions: list, language: str = "Vietnamese") -> GenerateQuizResponse:
    """
    Xử lý NHÓM 2: FILL_IN_THE_BLANK
    Schema riêng với BlankOption (blank_number, answer)
    
    :param context: str - The context or content based on which the quiz is to be generated.
    :param questions: list - A list of question configurations for fill-in-the-blank questions.
    :param language: str - The language in which the quiz should be generated.
    :return: GenerateQuizResponse - The generated quiz with fill-in-the-blank questions.
    """
    
    # Response schema cho fill-in-the-blank questions
    class FillBlankQuizResponse(BaseModel):
        questions: List[FillInTheBlankQuestion]
    
    llm = get_gemini_model(temperature=0.2)  # Thấp hơn vì cần chính xác hơn

    system_template = """
        You are an expert educational content generator specializing in FILL-IN-THE-BLANK QUESTIONS.

        STRICT OUTPUT REQUIREMENTS:
        - Output MUST be valid JSON.
        - MUST strictly follow the provided schema.
        - DO NOT add explanations, comments, or markdown.
        - DO NOT change field names or enum values.
        - DO NOT include text outside the JSON.
        - Provide tags based on question topics for categorization lowercase and without special characters
            (e.g., "oop", "data structures", "algorithms", "python", etc.) in the "tags" field.

        LANGUAGE REQUIREMENT:
        - All questions, options, and explanations (if any) must be written in the specified language.

        STRUCTURAL RULES FOR FILL_IN_THE_BLANK:

        - The question MUST contain numbered blanks in format: [___1___], [___2___], [___3___], etc.
        - Number of blanks by difficulty:
            + EASY difficulty: 2 blanks
            + MEDIUM difficulty: 3 blanks
            + HARD difficulty: 4 blanks
        - The "options" field contains a list of BlankOption objects.
        - Each BlankOption has:
            + "blank_number": integer starting from 1
            + "answer": correct answer string for that blank
        - Example:
            Question: "Python uses [___1___] for loop iteration and [___2___] for conditional statements."
            Options: [
                {{"blank_number": 1, "answer": "for"}},
                {{"blank_number": 2, "answer": "if"}}    
            ]
        - Answers should be specific, unambiguous terms.
        - Blanks should be evenly distributed throughout the question.

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

    parser = PydanticOutputParser(pydantic_object=FillBlankQuizResponse)

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
    result = chain.invoke(input_data)
    
    return GenerateQuizResponse(questions=result.questions)


async def generate_quiz_async(context: str, questions: list, language: str = "Vietnamese") -> GenerateQuizResponse:
    """
    Tạo quiz song song cho 2 nhóm câu hỏi:
    - NHÓM 1: SINGLE_CHOICE, MULTIPLE_CHOICE, TRUE_FALSE
    - NHÓM 2: FILL_IN_THE_BLANK
    
    Gọi song song bằng asyncio để tối ưu performance.
    Xử lý partial failure: nếu 1 nhóm fail không ảnh hưởng nhóm còn lại.
    
    :param context: str - The context or content based on which the quiz is to be generated.
    :param questions: list - A list of QuizTypeConfig configurations.
    :param language: str - The language in which the quiz should be generated.
    :return: GenerateQuizResponse - The complete generated quiz with shuffled options.
    """
    
    # Phân chia questions thành 2 nhóm dựa trên QuizType
    # questions là list of QuizTypeConfig objects, cần convert sang format phù hợp
    choice_configs = []
    fill_configs = []
    
    for q in questions:
        # Convert QuizTypeConfig to dict for LLM processing
        config_dict = {
            "type": q.type.value if hasattr(q.type, 'value') else q.type,
            "numberOfQuestions": [
                {
                    "difficulty": conf.difficulty.value if hasattr(conf.difficulty, 'value') else conf.difficulty,
                    "number": conf.number
                } for conf in q.numberOfQuestions
            ]
        }
        
        # Phân loại vào nhóm tương ứng
        if q.type.value == "FILL_IN_THE_BLANK":
            fill_configs.append(config_dict)
        else:
            choice_configs.append(config_dict)
    
    loop = asyncio.get_event_loop()
    tasks = []
    
    # Tạo tasks cho từng nhóm nếu có config
    if choice_configs:
        tasks.append(
            loop.run_in_executor(None, _generate_choice_questions, context, choice_configs, language)
        )
    if fill_configs:
        tasks.append(
            loop.run_in_executor(None, _generate_fill_blank_questions, context, fill_configs, language)
        )
    
    # Gọi song song
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Xử lý kết quả và partial failures
    all_questions = []
    errors = []
    
    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
        else:
            all_questions.extend(result.questions)
    
    # Nếu không có câu hỏi nào được tạo thành công, raise exception
    if not all_questions:
        error_msg = "; ".join(errors) if errors else "Failed to generate any questions"
        raise Exception(f"Quiz generation failed: {error_msg}")
    
    # Shuffle options và return
    return shuffle_quiz_options_all(GenerateQuizResponse(questions=all_questions))


def generate_quiz(context: str, questions: list, language: str = "Vietnamese") -> GenerateQuizResponse:
    """
    Synchronous wrapper cho generate_quiz_async.
    Dùng để maintain backward compatibility với code hiện tại.
    
    :param context: str - The context or content based on which the quiz is to be generated.
    :param questions: list - A list of question configurations.
    :param language: str - The language in which the quiz should be generated.
    :return: GenerateQuizResponse - The complete generated quiz.
    """
    return asyncio.run(generate_quiz_async(context, questions, language))