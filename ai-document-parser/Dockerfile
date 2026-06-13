FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    PYTHONPATH=/app/ai-document-parser/src:/app/shared-ai-lib/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry config virtualenvs.create false

COPY shared-ai-lib ./shared-ai-lib
COPY ai-document-parser ./ai-document-parser

WORKDIR /app/ai-document-parser

RUN poetry install --no-interaction --no-ansi --no-root

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "ai_document_parser.api.main:extract_document_app", "--host", "0.0.0.0", "--port", "8001"]