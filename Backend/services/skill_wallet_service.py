def get_skill_wallet(user_id: int):

    # dummy data for now
    dummy_users = {
        1: {
            "skills": ["Python", "Machine Learning", "Data Analysis"],
            "score": 88
        },
        2: {
            "skills": ["Electrical Repair", "Wiring", "Safety Inspection"],
            "score": 75
        },
        3: {
            "skills": ["Plumbing", "Pipe Installation", "Maintenance"],
            "score": 80
        }
    }

    user = dummy_users.get(user_id)

    if user:
        return {
            "user_id": user_id,
            "skills": user["skills"],
            "score": user["score"]
        }

    return {
        "user_id": user_id,
        "skills": [],
        "score": 0
    }