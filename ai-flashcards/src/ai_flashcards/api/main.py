# src/ai_flashcards/api/main.py
from fastapi import FastAPI
from ai_flashcards.api.routes import router

app = FastAPI(title="AI Flashcards Service")

app.include_router(router, prefix="/api/v1/flashcards")