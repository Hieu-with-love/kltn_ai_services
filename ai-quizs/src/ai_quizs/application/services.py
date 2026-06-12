import asyncio
from typing import List, Annotated, Union, Optional, Dict, Tuple
from pydantic import BaseModel, Field
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import PydanticOutputParser

from shared_ai.llm.gemini import get_gemini_model

from ..schema.quiz_response import (
    GenerateQuizResponse,
    SingleChoiceQuestion,
    MultipleChoiceQuestion,
    TrueFalseQuestion,
    FillInTheBlankQuestion,
)
from ..utils.quiz_utils import shuffle_quiz_options_all


# =====================================================================
# Prompt templates
# =====================================================================

CHOICE_SYSTEM_TEMPLATE = """
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

PER-CONFIG REQUIREMENTS:
- Generate EXACTLY the number of questions specified for each (type, difficulty) pair.
- Never mix types within a single question — "question_type" must match the requested "type".
- "answers" MUST be an empty array for SINGLE_CHOICE / MULTIPLE_CHOICE / TRUE_FALSE.

STRUCTURAL RULES BY QUESTION TYPE:
- SINGLE_CHOICE:   exactly 4 options ("text", "is_correct"); exactly 1 correct.
- MULTIPLE_CHOICE: exactly 4 options; at least 1 correct (2-3 for medium/hard).
- TRUE_FALSE:      exactly 2 options; exactly 1 correct.

Return ONLY valid JSON.
"""

CHOICE_HUMAN_TEMPLATE = """
Context:
{content_or_topic}

Question configuration:
{question_config_json}

Language: {language}

Output JSON schema:
{output_schema_json}
"""


FILL_SYSTEM_TEMPLATE = """
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
- All questions and answers must be written in the specified language.

PER-CONFIG REQUIREMENTS:
- Generate EXACTLY the number of questions specified for each (type, difficulty) pair.
- "options" MUST be an empty array (this type uses "answers" instead).

STRUCTURAL RULES FOR FILL_IN_THE_BLANK:
- The "question" MUST contain numbered blanks: [___1___], [___2___], [___3___], ...
- Number of blanks by difficulty: EASY=2, MEDIUM=3, HARD=4.
- "answers" is a list of {{"blank_number": int>=1, "answer": str}} — one entry per blank,
  numbered consecutively from 1.
- Answers must be specific and unambiguous.

Return ONLY valid JSON.
"""

FILL_HUMAN_TEMPLATE = """
Context:
{content_or_topic}

Question configuration:
{question_config_json}

Language: {language}

Output JSON schema:
{output_schema_json}
"""


# =====================================================================
# Count tracking helpers
# =====================================================================

def _expected_counts(configs: list) -> Dict[Tuple[str, str], int]:
    out: Dict[Tuple[str, str], int] = {}
    for cfg in configs:
        for c in cfg["numberOfQuestions"]:
            if c["number"] <= 0:
                continue
            key = (cfg["type"], c["difficulty"])
            out[key] = out.get(key, 0) + c["number"]
    return out


def _actual_counts(questions: list) -> Dict[Tuple[str, str], int]:
    out: Dict[Tuple[str, str], int] = {}
    for q in questions:
        key = (q.question_type, q.difficulty)
        out[key] = out.get(key, 0) + 1
    return out


def _missing_configs(
    expected: Dict[Tuple[str, str], int],
    actual: Dict[Tuple[str, str], int],
) -> list:
    by_type: Dict[str, list] = {}
    for (typ, diff), exp in expected.items():
        gap = exp - actual.get((typ, diff), 0)
        if gap <= 0:
            continue
        by_type.setdefault(typ, []).append({"difficulty": diff, "number": gap})
    return [{"type": t, "numberOfQuestions": items} for t, items in by_type.items()]


# =====================================================================
# LLM invocation
# =====================================================================

class _ChoiceQuizResponse(BaseModel):
    questions: List[
        Annotated[
            Union[SingleChoiceQuestion, MultipleChoiceQuestion, TrueFalseQuestion],
            Field(discriminator="question_type"),
        ]
    ]


class _FillBlankQuizResponse(BaseModel):
    questions: List[FillInTheBlankQuestion]


def _invoke_choice_chain(context, configs, language):
    llm = get_gemini_model(temperature=0.3)
    parser = PydanticOutputParser(pydantic_object=_ChoiceQuizResponse)
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(CHOICE_SYSTEM_TEMPLATE),
        HumanMessagePromptTemplate.from_template(CHOICE_HUMAN_TEMPLATE),
    ])
    chain = chat_prompt | llm | parser
    return chain.invoke({
        "content_or_topic": context,
        "question_config_json": configs,
        "language": language,
        "output_schema_json": parser.get_format_instructions(),
    })


def _invoke_fill_chain(context, configs, language):
    llm = get_gemini_model(temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=_FillBlankQuizResponse)
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(FILL_SYSTEM_TEMPLATE),
        HumanMessagePromptTemplate.from_template(FILL_HUMAN_TEMPLATE),
    ])
    chain = chat_prompt | llm | parser
    return chain.invoke({
        "content_or_topic": context,
        "question_config_json": configs,
        "language": language,
        "output_schema_json": parser.get_format_instructions(),
    })


# =====================================================================
# Group orchestrators (sync — run inside executors)
# =====================================================================

def _generate_choice_questions(context: str, configs: list, language: str) -> list:
    if not configs:
        return []
    expected = _expected_counts(configs)
    result = _invoke_choice_chain(context, configs, language)
    questions = list(result.questions)

    missing = _missing_configs(expected, _actual_counts(questions))
    if missing:
        try:
            retry = _invoke_choice_chain(context, missing, language)
            questions.extend(retry.questions)
        except Exception:
            pass
    return questions


def _generate_fill_blank_questions(context: str, configs: list, language: str) -> list:
    if not configs:
        return []
    expected = _expected_counts(configs)
    result = _invoke_fill_chain(context, configs, language)
    questions = list(result.questions)

    missing = _missing_configs(expected, _actual_counts(questions))
    if missing:
        try:
            retry = _invoke_fill_chain(context, missing, language)
            questions.extend(retry.questions)
        except Exception:
            pass
    return questions


# =====================================================================
# Public entry points
# =====================================================================

async def generate_quiz_async(
    context: str,
    questions: list,
    language: str = "vietnamese",
) -> GenerateQuizResponse:
    """
    Tạo quiz song song cho 2 nhóm câu hỏi:
    - NHÓM 1: SINGLE_CHOICE, MULTIPLE_CHOICE, TRUE_FALSE
    - NHÓM 2: FILL_IN_THE_BLANK
    """
    choice_configs: list = []
    fill_configs: list = []

    for q in questions:
        type_value = q.type.value if hasattr(q.type, "value") else q.type
        cfg = {
            "type": type_value,
            "numberOfQuestions": [
                {
                    "difficulty": (c.difficulty.value if hasattr(c.difficulty, "value") else c.difficulty),
                    "number": c.number,
                }
                for c in q.numberOfQuestions
                if c.number > 0
            ],
        }
        if not cfg["numberOfQuestions"]:
            continue
        if type_value == "FILL_IN_THE_BLANK":
            fill_configs.append(cfg)
        else:
            choice_configs.append(cfg)

    loop = asyncio.get_event_loop()
    tasks = []
    if choice_configs:
        tasks.append(loop.run_in_executor(
            None, _generate_choice_questions, context, choice_configs, language,
        ))
    if fill_configs:
        tasks.append(loop.run_in_executor(
            None, _generate_fill_blank_questions, context, fill_configs, language,
        ))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_questions: list = []
    errors: list = []
    for r in results:
        if isinstance(r, Exception):
            errors.append(str(r))
        else:
            all_questions.extend(r)

    if not all_questions:
        error_msg = "; ".join(errors) if errors else "Failed to generate any questions"
        raise Exception(f"Quiz generation failed: {error_msg}")

    return shuffle_quiz_options_all(GenerateQuizResponse(questions=all_questions))


def generate_quiz(
    context: str,
    questions: list,
    language: str = "vietnamese",
) -> GenerateQuizResponse:
    """Synchronous wrapper cho generate_quiz_async."""
    return asyncio.run(generate_quiz_async(context, questions, language))
