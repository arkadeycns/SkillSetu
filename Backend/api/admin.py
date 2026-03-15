from pathlib import Path

from fastapi import APIRouter, Form, HTTPException

from AI_Service.src.engine.question_bank import list_categories, reload_question_bank
from AI_Service.src.rag.indexer import INDEX_NAME, index_sops_from_file

router = APIRouter(prefix="/api/admin", tags=["Admin"])

BASE_DIR = Path(__file__).resolve().parents[1]
FIXED_INPUT_DIR = BASE_DIR / "data" / "admin_seed"
FIXED_QUESTION_BANK_PATH = FIXED_INPUT_DIR / "question_bank.fixed.json"
FIXED_SOP_PATH = FIXED_INPUT_DIR / "sop.fixed.txt"

def _validate_fixed_inputs() -> None:
    if not FIXED_QUESTION_BANK_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Question bank file not found at: {FIXED_QUESTION_BANK_PATH}",
        )
    if not FIXED_SOP_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail=f"SOP file not found at: {FIXED_SOP_PATH}",
        )

# Load question bank from fixed path
@router.post("/questions/upload")
async def upload_questions():
    _validate_fixed_inputs()

    try:
        active_path = reload_question_bank(path=str(FIXED_QUESTION_BANK_PATH))
        return {
            "message": "Question bank loaded from fixed path.",
            "active_question_bank_path": active_path,
            "categories": list_categories(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid question bank file: {exc}") from exc


# Reload question bank from fixed path
@router.post("/questions/reload")
async def reload_questions():
    _validate_fixed_inputs()

    try:
        active_path = reload_question_bank(path=str(FIXED_QUESTION_BANK_PATH))
        return {
            "message": "Question bank reloaded from fixed path.",
            "active_question_bank_path": active_path,
            "categories": list_categories(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to reload question bank: {exc}") from exc


# Index SOP document from fixed path
@router.post("/sops/index")
async def index_sops(batch_size: int = Form(25)):
    _validate_fixed_inputs()

    try:
        result = index_sops_from_file(file_path=str(FIXED_SOP_PATH), batch_size=batch_size)
        return {
            "message": "SOP indexed successfully from fixed path.",
            "source_file": FIXED_SOP_PATH.name,
            "index_name": INDEX_NAME,
            "chunks": result["chunks"],
            "upserted": result["upserted"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"SOP indexing failed: {exc}") from exc