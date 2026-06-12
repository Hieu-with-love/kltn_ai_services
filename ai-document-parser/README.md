# AI Document Parser Service

Trích xuất và phân tích nội dung tài liệu (PDF, DOCX, …) phục vụ các service AI khác.

**Port:** `8001`

## Yêu cầu

- Python >= 3.11
- [Poetry](https://python-poetry.org/docs/#installation)

## Cài đặt

```bash
# Cài shared-ai-lib trước (nếu chưa cài)
cd ../shared-ai-lib && poetry install && cd ../ai-document-parser

poetry install
```

## Chạy service

```bash
# Development (auto-reload)
poetry run uvicorn ai_document_parser.api.main:extract_document_app --reload --host localhost --port 8001

# Production
poetry run uvicorn ai_document_parser.api.main:extract_document_app --host localhost --port 8001
```

## API Docs

Sau khi chạy, truy cập: http://localhost:8001/docs
