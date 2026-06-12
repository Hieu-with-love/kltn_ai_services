# AI Quizs Service

Sinh câu hỏi quiz tự động (trắc nghiệm, đúng/sai, điền vào chỗ trống) từ nội dung do frontend cung cấp.

**Port:** `8003`

## Yêu cầu

- Python >= 3.11
- [Poetry](https://python-poetry.org/docs/#installation)

## Cài đặt

```bash
# Cài shared-ai-lib trước (nếu chưa cài)
cd ../shared-ai-lib && poetry install && cd ../ai-quizs

poetry install
```

## Chạy service

```bash
# Development (auto-reload)
poetry run uvicorn ai_quizs.api.main:app --reload --host localhost --port 8003

# Production
poetry run uvicorn ai_quizs.api.main:app --host localhost --port 8003
```

## API Docs

Sau khi chạy, truy cập: http://localhost:8003/docs
