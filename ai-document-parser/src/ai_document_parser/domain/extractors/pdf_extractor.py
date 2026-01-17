from pypdf import PdfReader
from io import BytesIO

def extract_pdf(file_bytes: bytes) -> tuple[str, int]:
    """
    Docstring for extract_pdf
    
    :param file_bytes: Bytes of the PDF file
    :type file_bytes: bytes
    :return: Extracted text and number of pages
    :rtype: tuple[str, int]
    """
    reader = PdfReader(BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""
    
    return text.strip(), len(reader.pages)