from langchain_core.prompts import ChatPromptTemplate
from shared_ai.llm.gemini import get_gemini_model

def generate_flashcards(content: str, n: int):
    prompt = ChatPromptTemplate.from_template("""
    Bạn là giảng viên đại học.
    Tạo {n} flashcards từ nội dung sau bằng ngôn ngữ {language}.

    Nội dung:
    {content}

    Format:
    - Front:
    - Back:
    """)

    llm = get_gemini_model(temperature=0.3)

    chain = prompt | llm
    response = chain.invoke({
        "content": content,
        "n": n,
        "language": "vietnamese"
    })

    return response.content
