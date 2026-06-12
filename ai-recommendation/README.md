# AI Recommendation Service

Gợi ý nội dung học tập cá nhân hoá cho người dùng.

**Port:** `8004`

## Yêu cầu

- Python >= 3.11
- [Poetry](https://python-poetry.org/docs/#installation)

## Cài đặt

```bash
poetry install
```

## Chạy service

```bash
# Development (auto-reload)
PYTHONPATH=src poetry run uvicorn ai_recommendation.main:app --reload --host localhost --port 8004

# Production
PYTHONPATH=src poetry run uvicorn ai_recommendation.main:app --host localhost --port 8004

# Hoặc dùng run.py có sẵn
poetry run python run.py
```

## API Docs

Sau khi chạy, truy cập: http://localhost:8004/docs
