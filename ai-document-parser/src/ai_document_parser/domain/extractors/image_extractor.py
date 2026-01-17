from PIL import Image
from io import BytesIO
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_image(file_bytes: bytes, lang="vie") -> str:
    """
    Extract text from an image file using OCR (Optical Character Recognition).
    
    :param file_bytes: Bytes of the image file
    :type file_bytes: bytes
    :param lang: Language for OCR, default is Vietnamese ('vie')
    :type lang: str
    :return: Extracted text
    :rtype: str
    """
    image = Image.open(BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)
    return text.strip()