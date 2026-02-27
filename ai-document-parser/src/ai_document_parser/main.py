from fastapi import FastAPI
from .api.routes import router as document_router

app = FastAPI(title="AI Document Parser")

app.include_router(document_router)
