from .extractors.pdf_extractor import extract_pdf
from .extractors.image_extractor import extract_image

class DocumentService:
    
    @staticmethod
    def extract(file_name: str, file_bytes: bytes):
        extension = file_name.split('.')[-1].lower()

        if extension == 'pdf':
            text, pages = extract_pdf(file_bytes)
            return text, pages, 'pdf'
        
        if extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']:
            text = extract_image(file_bytes)
            return text, 1, 'image'
        
        raise ValueError(f"Unsupported file extension: {extension}")

    def extract_summary(file_name: str, file_bytes: bytes) -> str:
        text,_ = DocumentService.extract(file_name, file_bytes)
        # call the method to summarize text
        
        