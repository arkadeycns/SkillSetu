"""Question bank loader for category-wise vocational assessments."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

DEFAULT_QUESTION_BANK_PATH = "data/question_bank.json"


@dataclass(frozen=True)
class QuestionItem:
    id: str
    text: str


@dataclass(frozen=True)
class CategoryItem:
    id: str
    title: str
    questions: List[QuestionItem]


def get_question_bank_path() -> str:
    return os.environ.get("QUESTION_BANK_PATH", DEFAULT_QUESTION_BANK_PATH)


@lru_cache(maxsize=1)
def _load_bank(path: str) -> Dict[str, List[CategoryItem]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Question bank file not found: {path}")

    raw = json.loads(source.read_text(encoding="utf-8"))
    categories: List[CategoryItem] = []

    for category in raw.get("categories", []):
        questions = [
            QuestionItem(id=str(question["id"]), text=str(question["text"]))
            for question in category.get("questions", [])
            if question.get("id") and question.get("text")
        ]
        categories.append(
            CategoryItem(
                id=str(category["id"]),
                title=str(category.get("title", category["id"])),
                questions=questions,
            )
        )

    if not categories:
        raise ValueError("Question bank has no categories.")

    return {"categories": categories}


def reload_question_bank(path: str | None = None) -> str:
    effective_path = path or get_question_bank_path()
    if path:
        os.environ["QUESTION_BANK_PATH"] = path

    _load_bank.cache_clear()
    _load_bank(effective_path)
    return effective_path


def list_categories() -> List[Dict[str, str]]:
    bank = _load_bank(get_question_bank_path())
    return [{"id": c.id, "title": c.title} for c in bank["categories"]]


def get_category_questions(category_id: str) -> List[QuestionItem]:
    bank = _load_bank(get_question_bank_path())
    for category in bank["categories"]:
        if category.id == category_id:
            if len(category.questions) != 10:
                raise ValueError(
                    f"Category '{category_id}' must contain exactly 10 questions; found {len(category.questions)}."
                )
            return category.questions
    raise KeyError(f"Unknown category: {category_id}")
