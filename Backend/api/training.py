from fastapi import APIRouter
from services.data_provider import get_user_resume_data
from services.ai_engine import generate_training_recommendations

router = APIRouter(prefix="/api/training", tags=["Training"])

@router.post("/recommend")
async def recommend(data: dict):

    user_data = get_user_resume_data(
        user_id=data.get("user_id"),
        resume_text=data.get("resume_text")
    )

    return {
        "success": True,
        "data": generate_training_recommendations(user_data)
    }