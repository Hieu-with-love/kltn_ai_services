from fastapi import FastAPI
from .api.document import router as document_router

app = FastAPI(title="AI Document Parser")

app.include_router(document_router)
