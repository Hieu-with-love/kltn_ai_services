from fastapi import FastAPI
from .routes import router

app = FastAPI(title="AI Quiz Service")

app.include_router(router, prefix="/api/v1/quiz", tags=["Quiz Generation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)