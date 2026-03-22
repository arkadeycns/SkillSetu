from fastapi import APIRouter, HTTPException
from services.user_service import update_user_profile
from core.database import get_db

router = APIRouter()

# GET: Fetch a specific user's Profile
@router.get("/{clerk_id}")
async def get_profile(clerk_id: str):
    db = get_db()
    user = await db.users.find_one({"clerk_id": clerk_id})
    if not user:
        # Clean default structure (No more fake balances!)
        return {"skills": [], "activity_log": [], "role": "Worker"}
    
    user["_id"] = str(user["_id"])
    return user

# POST: Update profile (called after an AI assessment)
@router.post("/update")
async def update_profile(data: dict):
    clerk_id = data.get("clerk_id")
    if not clerk_id:
        raise HTTPException(status_code=400, detail="Missing clerk_id")
    
    result = await update_user_profile(clerk_id, data)
    return result