from pydantic import BaseModel

class DocumentExtractResponse(BaseModel):
    text: str
    pages: int | None = None
    sourceType: str
