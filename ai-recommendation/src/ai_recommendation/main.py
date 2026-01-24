from fastapi import FastAPI
from dotenv import load_dotenv
from ai_recommendation.api.routes import router

load_dotenv()

app = FastAPI(title="AI Course Recommendation Service")

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
