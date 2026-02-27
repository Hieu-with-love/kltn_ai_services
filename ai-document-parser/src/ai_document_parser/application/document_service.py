from ..domain.extractors.pdf_extractor import extract_pdf
from ..domain.extractors.image_extractor import extract_image
from ..domain.summarier.document_summary import summarize_document

"""
This service class is responsible for handling the core logic of document extraction and summarization.
"""
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

    @staticmethod
    async def extract_summary(file_name: str, file_bytes: bytes) -> str:
        text, _, _ = DocumentService.extract(file_name, file_bytes)
        # call the method to summarize text
        return await summarize_document(text)
        
        
        