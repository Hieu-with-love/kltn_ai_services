"""Tests for the /generate endpoint covering the new learning-outcomes flow."""
from collections import Counter

import pytest
from fastapi.testclient import TestClient

from ai_quizs.api.main import app
from ai_quizs.application import services as svc
from ai_quizs.schema.quiz_response import (
    BlankOption,
    ChoiceOption,
    FillInTheBlankQuestion,
    MultipleChoiceQuestion,
    SingleChoiceQuestion,
    TrueFalseQuestion,
)

GENERATE_URL = "/api/v1/quiz/generate"
client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers to build canned LLM outputs for monkeypatching
# ---------------------------------------------------------------------------

def _choice_q(kind, difficulty, lo_id):
    if kind == "TRUE_FALSE":
        opts = [
            ChoiceOption(text="Đúng", is_correct=True),
            ChoiceOption(text="Sai", is_correct=False),
        ]
        cls = TrueFalseQuestion
    else:
        opts = [
            ChoiceOption(text="A", is_correct=True),
            ChoiceOption(text="B", is_correct=False),
            ChoiceOption(text="C", is_correct=False),
            ChoiceOption(text="D", is_correct=False),
        ]
        cls = SingleChoiceQuestion if kind == "SINGLE_CHOICE" else MultipleChoiceQuestion
    return cls(
        question=f"Q[{kind}/{difficulty}]",
        difficulty=difficulty,
        learning_outcome_id=lo_id,
        options=opts,
    )


def _fill_q(difficulty, lo_id, blanks=2):
    return FillInTheBlankQuestion(
        question="Python dùng [___1___] cho vòng lặp và [___2___] cho điều kiện.",
        difficulty=difficulty,
        learning_outcome_id=lo_id,
        answers=[
            BlankOption(blank_number=i + 1, answer=f"a{i + 1}") for i in range(blanks)
        ],
    )


class _Resp:
    def __init__(self, questions):
        self.questions = questions


# ---------------------------------------------------------------------------
# Test 1 — outcomes + 3 choice types, 2 EASY + 1 MEDIUM + 0 HARD each = 9 questions
# ---------------------------------------------------------------------------

def test_outcomes_with_three_choice_types(monkeypatch):
    lo_ids = ["lo_c1", "lo_c2"]
    # Build 9 questions: for each of (SINGLE, MULTIPLE, TRUE_FALSE):
    # 2 EASY + 1 MEDIUM, round-robin across the 2 outcome ids.
    built = []
    idx = 0
    for kind in ["SINGLE_CHOICE", "MULTIPLE_CHOICE", "TRUE_FALSE"]:
        for difficulty in ["EASY", "EASY", "MEDIUM"]:
            built.append(_choice_q(kind, difficulty, lo_ids[idx % 2]))
            idx += 1

    monkeypatch.setattr(svc, "_invoke_choice_chain", lambda *a, **kw: _Resp(built))

    payload = {
        "context": "Bối cảnh tổng quát.",
        "learning_outcomes": [
            {"id": "lo_c1", "title": "Outcome Một", "content": "Nội dung 1"},
            {"id": "lo_c2", "title": "Outcome Hai", "content": "Nội dung 2"},
        ],
        "questions": [
            {"type": "SINGLE_CHOICE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 2},
                {"difficulty": "MEDIUM", "number": 1},
                {"difficulty": "HARD", "number": 0},
            ]},
            {"type": "MULTIPLE_CHOICE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 2},
                {"difficulty": "MEDIUM", "number": 1},
                {"difficulty": "HARD", "number": 0},
            ]},
            {"type": "TRUE_FALSE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 2},
                {"difficulty": "MEDIUM", "number": 1},
                {"difficulty": "HARD", "number": 0},
            ]},
        ],
        "language": "vietnamese",
    }

    r = client.post(GENERATE_URL, json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    qs = body["data"]["questions"]
    assert len(qs) == 9

    # Every question carries an outcome id from the request,
    # and the service backfills learning_outcome_title from the roster.
    for q in qs:
        assert q["learning_outcome_id"] in lo_ids
        assert q["learning_outcome_title"] in ("Outcome Một", "Outcome Hai")

    counts = Counter((q["question_type"], q["difficulty"]) for q in qs)
    for kind in ("SINGLE_CHOICE", "MULTIPLE_CHOICE", "TRUE_FALSE"):
        assert counts[(kind, "EASY")] == 2
        assert counts[(kind, "MEDIUM")] == 1
        assert counts[(kind, "HARD")] == 0


# ---------------------------------------------------------------------------
# Test 2 — backward compat: only `context` (no learning_outcomes)
# ---------------------------------------------------------------------------

def test_context_only_backward_compat(monkeypatch):
    built = [_choice_q("SINGLE_CHOICE", "EASY", None) for _ in range(3)]
    monkeypatch.setattr(svc, "_invoke_choice_chain", lambda *a, **kw: _Resp(built))

    payload = {
        "context": "Lập trình hướng đối tượng trong Java.",
        "questions": [
            {"type": "SINGLE_CHOICE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 3},
            ]},
        ],
    }

    r = client.post(GENERATE_URL, json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    qs = body["data"]["questions"]
    assert len(qs) == 3
    for q in qs:
        assert q["learning_outcome_id"] is None
        assert q["learning_outcome_title"] is None


# ---------------------------------------------------------------------------
# Test 3 — total numberOfQuestions == 0 → HTTP 400
# ---------------------------------------------------------------------------

def test_total_zero_returns_400():
    payload = {
        "context": "anything",
        "questions": [
            {"type": "SINGLE_CHOICE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 0},
                {"difficulty": "MEDIUM", "number": 0},
            ]},
        ],
    }
    r = client.post(GENERATE_URL, json=payload)
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Test 4 — FILL_IN_THE_BLANK populates `answers`, leaves `options` empty
# ---------------------------------------------------------------------------

def test_fill_in_the_blank_has_answers_empty_options(monkeypatch):
    built = [_fill_q("EASY", "lo_1", blanks=2)]
    monkeypatch.setattr(svc, "_invoke_fill_chain", lambda *a, **kw: _Resp(built))

    payload = {
        "context": "",
        "learning_outcomes": [
            {"id": "lo_1", "title": "Cấu trúc điều khiển", "content": "for/if"},
        ],
        "questions": [
            {"type": "FILL_IN_THE_BLANK", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 1},
            ]},
        ],
    }

    r = client.post(GENERATE_URL, json=payload)
    assert r.status_code == 200, r.text
    out = r.json()["data"]["questions"][0]
    assert out["question_type"] == "FILL_IN_THE_BLANK"
    assert out["options"] == []
    assert len(out["answers"]) == 2
    assert out["answers"][0]["blank_number"] == 1
    assert out["learning_outcome_id"] == "lo_1"
    assert out["learning_outcome_title"] == "Cấu trúc điều khiển"


# ---------------------------------------------------------------------------
# Test 5 — fill-missing retry: first LLM call returns too few; second call fills the gap
# ---------------------------------------------------------------------------

def test_fill_missing_retry(monkeypatch):
    # Request: 3 EASY SINGLE_CHOICE, but first call only returns 1.
    first = [_choice_q("SINGLE_CHOICE", "EASY", "lo_1")]
    second = [_choice_q("SINGLE_CHOICE", "EASY", "lo_1") for _ in range(2)]

    calls = {"n": 0}

    def fake(*args, **kwargs):
        calls["n"] += 1
        return _Resp(first if calls["n"] == 1 else second)

    monkeypatch.setattr(svc, "_invoke_choice_chain", fake)

    payload = {
        "learning_outcomes": [
            {"id": "lo_1", "title": "Outcome", "content": "x"},
        ],
        "questions": [
            {"type": "SINGLE_CHOICE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 3},
            ]},
        ],
    }
    r = client.post(GENERATE_URL, json=payload)
    assert r.status_code == 200, r.text
    qs = r.json()["data"]["questions"]
    assert len(qs) == 3
    assert calls["n"] == 2  # retry happened exactly once


# ---------------------------------------------------------------------------
# Test 6 — empty title in learning_outcomes → 422 (Pydantic validation)
# ---------------------------------------------------------------------------

def test_empty_outcome_title_rejected():
    payload = {
        "learning_outcomes": [{"id": "lo_x", "title": "  ", "content": ""}],
        "questions": [
            {"type": "SINGLE_CHOICE", "numberOfQuestions": [
                {"difficulty": "EASY", "number": 2},
            ]},
        ],
    }
    r = client.post(GENERATE_URL, json=payload)
    assert r.status_code == 422
