import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from AI_Service.src.engine.question_bank import (
    get_category_questions,
    list_categories,
    reload_question_bank,
)
from AI_Service.src.rag.indexer import index_sops_from_file

BASE_DIR = Path(__file__).resolve().parents[1]
FIXED_INPUT_DIR = BASE_DIR / "data" / "admin_seed"
FIXED_QUESTION_BANK_PATH = FIXED_INPUT_DIR / "question_bank.fixed.json"
FIXED_SOP_PATH = FIXED_INPUT_DIR / "sop.fixed.txt"
SOP_STATE_PATH = FIXED_INPUT_DIR / ".sop_index_state.json"

_QUESTION_CURSOR: dict[str, int] = {}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_state() -> dict:
    if not SOP_STATE_PATH.exists():
        return {}
    try:
        return json.loads(SOP_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    FIXED_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    SOP_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def ensure_ai_service_ready(batch_size: int = 25) -> dict:
    if not FIXED_QUESTION_BANK_PATH.exists():
        raise FileNotFoundError(f"Missing fixed question bank: {FIXED_QUESTION_BANK_PATH}")
    if not FIXED_SOP_PATH.exists():
        raise FileNotFoundError(f"Missing fixed SOP file: {FIXED_SOP_PATH}")

    os.environ["QUESTION_BANK_PATH"] = str(FIXED_QUESTION_BANK_PATH)
    active_question_bank_path = reload_question_bank(path=str(FIXED_QUESTION_BANK_PATH))

    sop_hash = _sha256_file(FIXED_SOP_PATH)
    state = _load_state()
    should_index = state.get("sop_hash") != sop_hash

    if should_index:
        index_result = index_sops_from_file(file_path=str(FIXED_SOP_PATH), batch_size=batch_size)
        _save_state(
            {
                "sop_hash": sop_hash,
                "source_file": str(FIXED_SOP_PATH),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "chunks": index_result.get("chunks", 0),
                "upserted": index_result.get("upserted", 0),
            }
        )
    else:
        index_result = {
            "chunks": state.get("chunks", 0),
            "upserted": 0,
            "skipped": True,
        }

    return {
        "question_bank_path": active_question_bank_path,
        "sop_path": str(FIXED_SOP_PATH),
        "index": index_result,
    }


def get_next_assessment_question(category_id: str | None = None) -> str:
    categories = list_categories()
    if not categories:
        raise ValueError("No categories available in question bank.")

    chosen_category = category_id or os.environ.get("DEFAULT_CATEGORY_ID") or categories[0]["id"]
    questions = get_category_questions(chosen_category)
    if not questions:
        raise ValueError(f"No questions available for category: {chosen_category}")

    current_index = _QUESTION_CURSOR.get(chosen_category, 0) % len(questions)
    _QUESTION_CURSOR[chosen_category] = (current_index + 1) % len(questions)
    return questions[current_index].text
