"""
Entry point to run the AI Quiz Service
"""
import uvicorn
from ai_quizs.api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
