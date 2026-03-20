def get_user_resume_data(user_id=None, resume_text=None):
    """
    Dynamic user data (demo-level intelligent parsing)
    Supports:
    - resume-based users (skilled)
    - no-resume users (informal)
    """

    text = (resume_text or "").lower()

    # ==========================================================
    #  ROLE DETECTION (BLUE COLLAR)
    # ==========================================================

    if "electrician" in text:
        return {
            "role": "electrician",
            "skills": ["wiring", "circuits", "safety"],
            "experience_level": "intermediate"
        }

    elif "carpenter" in text:
        return {
            "role": "carpenter",
            "skills": ["cutting", "measurement", "tools"],
            "experience_level": "beginner"
        }

    elif "mechanic" in text:
        return {
            "role": "mechanic",
            "skills": ["engine repair", "tools", "maintenance"],
            "experience_level": "intermediate"
        }

    elif "plumber" in text:
        return {
            "role": "plumber",
            "skills": ["pipes", "fittings", "leak fixing"],
            "experience_level": "beginner"
        }

    # ==========================================================
    #  FALLBACK (TECH USERS)
    # ==========================================================

    elif "developer" in text or "software" in text:
        return {
            "role": "developer",
            "skills": ["arrays", "c++"],
            "experience_level": "beginner"
        }

    # ==========================================================
    #  NO RESUME (INFORMAL USERS)
    # ==========================================================

    return {
        "role": "general_worker",
        "skills": ["basic work"],
        "experience_level": "beginner"
    }