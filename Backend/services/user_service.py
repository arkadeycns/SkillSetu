from core.database import get_db
from datetime import datetime

async def update_user_profile(clerk_id: str, data: dict):
    db = get_db()
    
    # Extract the data sent from the React frontend
    user_name = data.get("user_name", "Unknown Worker")
    skill_name = data.get("skill_name", "General Trade")
    score = data.get("score", 0)
    result = data.get("result", "FAIL")
    state = data.get("state", "Unknown")
    badges = data.get("badges", [])
    
    # Exactly matching your Dashboard's $project structure!
    activity_entry = {
        "name": user_name,
        "skill": skill_name,
        "result": result,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now() # Used by the backend to sort newest to oldest
    }
    
    # 2. The Skill Entry for the Digital Wallet
    skill_entry = {
        "skill_name": skill_name,
        "score": score,
        "result": result,
        "status": "Verified" if result == "PASS" else "Learning",
        "badges": badges
    }
    
    # 3. Update the Database
    # First, update the general info and remove the old skill (so we don't have duplicates if they test twice)
    await db.users.update_one(
        {"clerk_id": clerk_id},
        {
            "$set": {
                "name": user_name,
                "state": state,
                "last_active": datetime.now(),
                "role": "Worker"
            },
            "$pull": {
                "skills": {"skill_name": skill_name}
            }
        },
        upsert=True
    )
    
    # Finally, push the new skill score and the new activity log to the arrays
    await db.users.update_one(
        {"clerk_id": clerk_id},
        {
            "$push": {
                "skills": skill_entry,
                "activity_log": activity_entry
            }
        }
    )
    
    return {"success": True, "message": "Profile updated perfectly"}