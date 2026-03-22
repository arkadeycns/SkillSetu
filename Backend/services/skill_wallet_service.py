from services.db import skills_collection

def get_skill_wallet(user_id: str):

    # Fetch all skills for this user
    skills = list(
        skills_collection.find({"user_id": user_id}, {"_id": 0})
    )

    # If no skills found
    if not skills:
        return {
            "user_id": user_id,
            "skills": [],
            "score": 0
        }

    # Calculate average score (optional logic)
    avg_score = sum(skill.get("trust", 0) for skill in skills) / len(skills)

    return {
        "user_id": user_id,
        "skills": skills,
        "score": round(avg_score)
    }