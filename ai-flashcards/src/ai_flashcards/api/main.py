# src/ai_flashcards/api/main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(_: Request, exc: RequestValidationError):
    # Spring client expects {"detail": "<message>"} so it can map to AiServiceException.
    errors = exc.errors() or []
    if errors:
        first = errors[0]
        loc_parts = [str(p) for p in first.get("loc", ()) if p != "body"]
        location = ".".join(loc_parts)
        msg = first.get("msg", "Invalid request")
        detail = f"{location}: {msg}" if location else msg
    else:
        detail = "Invalid request"
    return JSONResponse(status_code=422, content={"detail": detail})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
