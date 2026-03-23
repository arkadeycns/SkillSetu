from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from services.data_provider import get_user_resume_data
from AI_Service.src.engine.ai_engine import generate_training_recommendations

router = APIRouter(tags=["Training"])

class TrainingRequest(BaseModel):
    user_id: str
    resume_text: Optional[str] = None
    role: Optional[str] = None
    skills: Optional[List[str]] = []
    language: Optional[str] = "en"
    strengths: Optional[List[str]] = []
    gaps: Optional[List[str]] = []

@router.post("/recommend")
async def recommend(request: TrainingRequest):

    # Pass the fully enriched payload to the data provider
    user_data = get_user_resume_data(
        user_id=request.user_id,
        resume_text=request.resume_text,
        role=request.role,
        skills=request.skills,
        language=request.language,
        strengths=request.strengths,
        gaps=request.gaps
    )

    return {
        "success": True,
        "data": generate_training_recommendations(user_data)
    }