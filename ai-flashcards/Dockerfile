FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    PYTHONPATH=/app/ai-flashcards/src:/app/shared-ai-lib/src

WORKDIR /app

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry config virtualenvs.create false

COPY shared-ai-lib ./shared-ai-lib
COPY ai-flashcards ./ai-flashcards

WORKDIR /app/ai-flashcards

RUN poetry install --no-interaction --no-ansi --no-root

EXPOSE 8002

CMD ["python", "-m", "uvicorn", "ai_flashcards.api.main:app", "--host", "0.0.0.0", "--port", "8002"]