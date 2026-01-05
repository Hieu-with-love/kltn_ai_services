from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_gemini_model(temperature: float = 0.3):
    """Get Gemini model from Langchain.

    Args:
        temperature (float, optional): Temperature for the model. Defaults to 0.3.

    Returns:
        ChatGoogleGenerativeAI: Gemini model instance.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature
    )