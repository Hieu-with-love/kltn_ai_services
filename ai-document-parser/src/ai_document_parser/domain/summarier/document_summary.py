from shared_ai.llm.gemini import get_gemini_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio
from fastapi.responses import StreamingResponse

"""
Summarize a document using an LLM. That LLM is Gemini.

:param document_text: The text content of the document to summarize.
:return: A summary of the document.
:raises Exception: If there's an error communicating with the LLM.
"""
async def summarize_document(document_text: str, language: str = "English") -> StreamingResponse:
    """
    Asynchronously summarize a document using Gemini LLM with streaming response.
    
    :param document_text: The text content of the document to summarize.
    :param language: The language for the summary output (default: English).
    :return: A StreamingResponse that streams the summary.
    :raises ValueError: If document text is empty.
    :raises Exception: If there's an error communicating with the LLM.
    """
    if not document_text or not document_text.strip():
        raise ValueError("Document text cannot be empty")
    
    prompt = PromptTemplate(
        input_variables=["text", "language"],
        template=(
            "Summarize the following document into one short paragraph that captures only the main ideas. "
            "Do not add headings, labels, or introductory phrases. "
            "Write the summary in {language}. "
            "Return only the summary text.\n\n"
            "{text}"
        ),
    )

    # Get Gemini model instance
    llm = get_gemini_model(temperature=0.3)
    chain = prompt | llm | StrOutputParser()

    async def stream_generator():
        """Generate streaming chunks from the LLM response."""
        try:
            async for chunk in chain.astream({"text": document_text, "language": language}):
                yield chunk
        except Exception as e:
            error_msg = f"Error summarizing document with LLM: {str(e)}"
            yield error_msg
    
    return StreamingResponse(stream_generator(), media_type="text/plain")
