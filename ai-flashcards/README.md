# AI Flashcards Service

Sinh flashcard tự động từ nội dung tài liệu dựa trên cấu hình độ khó từ frontend.

**Port:** `8002`

## Yêu cầu

- Python >= 3.11
- [Poetry](https://python-poetry.org/docs/#installation)

## Cài đặt

```bash
# Cài shared-ai-lib trước (nếu chưa cài)
cd ../shared-ai-lib && poetry install && cd ../ai-flashcards

poetry install
```

## Chạy service

```bash
# Development (auto-reload)
poetry run uvicorn ai_flashcards.api.main:app --reload --host localhost --port 8002

# Production
poetry run uvicorn ai_flashcards.api.main:app --host localhost --port 8002
```

## API Docs

Sau khi chạy, truy cập: http://localhost:8002/docs
