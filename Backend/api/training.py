from fastapi import APIRouter
from services.data_provider import get_user_resume_data
from services.ai_engine import generate_training_recommendations

router = APIRouter()


@router.post("/recommend")
async def recommend_training(data: dict):
    try:
        user_id = data.get("user_id")
        resume_text = data.get("resume_text")

        # 🔹 Get user data (mock or resume-based)
        user_data = get_user_resume_data(
            user_id=user_id,
            resume_text=resume_text
        )

        # 🔹 Generate recommendations using AI
        recommendations = generate_training_recommendations(user_data)

        return {
            "success": True,
            "data": recommendations
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }