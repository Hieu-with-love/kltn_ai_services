# kltn-ai-services

A Python-based microservices suite providing AI-powered features for an e-learning platform. Each service exposes a FastAPI REST API and is backed by Google Gemini 2.5-Flash via LangChain. The services are designed to integrate with a Spring Boot backend.

## Services

| Service | Port | Description |
|---------|------|-------------|
| [ai-document-parser](ai-document-parser/) | 8001 | Extracts and summarizes content from PDF and DOCX files |
| [ai-flashcards](ai-flashcards/) | 8002 | Generates flashcards from document content |
| [ai-quizs](ai-quizs/) | 8003 | Generates quiz questions (multiple-choice, true/false, fill-in-the-blank) |
| [ai-recommendation](ai-recommendation/) | 8004 | Returns personalized course recommendations based on user profiles |
| [shared-ai-lib](shared-ai-lib/) | — | Shared LLM client, prompt templates, schemas, and utilities |

## Architecture

```
kltn-ai-services/
├── shared-ai-lib/          # Shared library (install first)
├── ai-document-parser/
├── ai-flashcards/
├── ai-quizs/
└── ai-recommendation/
```

Each service follows a layered structure:

```
src/<service>/
├── api/           # FastAPI app, routes, and request/response schemas
├── application/   # Business logic and service orchestration
├── domain/        # Core generation logic (LLM calls)
├── schema/        # Pydantic models
├── config/        # Settings and environment loading
└── utils/         # Helpers
```

## Tech Stack

- **Runtime**: Python 3.11+
- **Web framework**: FastAPI + Uvicorn
- **LLM orchestration**: LangChain
- **AI model**: Google Gemini 2.5-Flash (`langchain-google-genai`)
- **Validation**: Pydantic v2
- **Package management**: Poetry

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- A Google API key with Gemini access

## Getting Started

### 1. Install the shared library

```bash
cd shared-ai-lib
poetry install
```

### 2. Configure environment variables

Copy `.env.example` to `.env` inside each service directory and fill in your key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Install and run a service

```bash
cd ai-document-parser     # or ai-flashcards / ai-quizs / ai-recommendation
poetry install
poetry run uvicorn ai_document_parser.api.main:extract_document_app --reload --port 8001
```

Repeat for each service on its designated port.

| Service | Uvicorn target | Port |
|---------|---------------|------|
| ai-document-parser | `ai_document_parser.api.main:extract_document_app` | 8001 |
| ai-flashcards | `ai_flashcards.api.main:app` | 8002 |
| ai-quizs | `ai_quizs.api.main:app` | 8003 |
| ai-recommendation | `ai_recommendation.main:app` | 8004 |

> For ai-recommendation, prefix the command with `PYTHONPATH=src`.

### 4. Explore the API

Once a service is running, interactive API docs are available at:

```
http://localhost:<port>/docs
```

## API Summary

### ai-document-parser — `/api/v1/parser`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/document` | Extract text from an uploaded PDF or DOCX file |
| POST | `/summarize` | Summarize content from an uploaded document |

### ai-flashcards — `/api/v1/flashcards`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate` | Generate flashcards from provided text content |

### ai-quizs — `/api/v1/quiz`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate` | Generate quiz questions from content; supports `SINGLE_CHOICE`, `MULTIPLE_CHOICE`, `TRUE_FALSE`, `FILL_IN_THE_BLANK` types and a `language` parameter |

### ai-recommendation — `/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/recommend` | Return personalized course recommendations for a user profile |

## Running Tests

```bash
cd <service>
poetry run pytest
```

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/my-feature`).
3. Commit your changes.
4. Open a pull request against `main`.
