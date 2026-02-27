from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from ..application.document_service import DocumentService
from ..schema.document_schema import DocumentExtractResponse

router = APIRouter()

@router.post("/document", response_model=DocumentExtractResponse)
async def extract_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        text, pages, doc_type = DocumentService.extract(file.filename, file_bytes)

        return DocumentExtractResponse(text=text, pages=pages, sourceType=doc_type)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.post("/summarize", response_model=str)
async def summarize_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        summary = await DocumentService.extract_summary(file.filename, file_bytes)

        return summary
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))