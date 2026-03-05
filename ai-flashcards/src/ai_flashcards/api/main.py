# src/ai_flashcards/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_flashcards.api.routes import router

app = FastAPI(title="AI Flashcards Service")

app.include_router(router, prefix="/api/v1/flashcards")

# Permit calling the API directly from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # chỉnh lại domain FE khi deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)