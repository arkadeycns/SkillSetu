from pathlib import Path
from fastapi import APIRouter, Form, HTTPException

# --- Existing AI Service Imports ---
from AI_Service.src.engine.question_bank import list_categories, reload_question_bank
from AI_Service.src.rag.indexer import INDEX_NAME, index_sops_from_file

# --- New Stats Service Import ---
from services.admin_service import get_national_stats

# CRITICAL FIX: Removed prefix="/api/admin" here because main.py already does it!
router = APIRouter()

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


# ==========================================
# 1. AI ENGINE ROUTES (Existing)
# ==========================================

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


# ==========================================
# 2. COMMAND CENTER / STATS ROUTE (New)
# ==========================================

@router.get("/stats")
async def get_stats():
    """
    Returns data for the React Dashboard and Regional Heatmap:
    - totalWorkers: (int)
    - liveFeed: (List of Pass/Fail records)
    - heatmapData: (List of {id: "State", count: 10})
    """
    stats = await get_national_stats()
    return stats