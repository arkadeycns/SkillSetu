from fastapi import APIRouter
from services.db import users_collection

router = APIRouter(prefix="/api/user", tags=["User"])

@router.post("/save")
def save_user(data: dict):
    users_collection.update_one(
        {"clerkId": data["clerkId"]},
        {"$set": data},
        upsert=True
    )
    return {"message": "User saved successfully"}