from shared_ai.llm import gemini
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory

def summarize_document(document_text):
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Summarize the following document:\n\n{text}\n\nSummary:",
    )

    chain = gemini | prompt

    summary = chain.invoke({"text": document_text})

    return summary
