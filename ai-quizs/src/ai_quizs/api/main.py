from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import router

app = FastAPI(title="AI Quiz Service")

# Global exception handler để chuẩn hóa error response
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler để đảm bảo response contract nhất quán.
    Trả về error response với format chuẩn kể cả khi có lỗi.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "partial_results": None
            }
        }
    )

app.include_router(router, prefix="/api/v1/quiz", tags=["Quiz Generation"])

app.add_middleware (
    CORSMiddleware,
    allow_origins=["http://localhost:8888"], # Chỉ cho phép Gateway Spring Boot truy cập.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)