from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

extract_document_app = FastAPI(title="AI Document Parser API", version="1.0")

extract_document_app.include_router(router, prefix="/api/v1/parser", tags=["Extract Document"])

# Permit calling the API directly from browser
extract_document_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # chỉnh lại domain FE khi deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(extract_document_app, host="0.0.0.0", port=8000)