def get_user_resume_data(
    user_id=None, 
    resume_text=None, 
    role=None, 
    skills=None, 
    language="en", 
    strengths=None, 
    gaps=None
):
    """
    Dynamic user data profile builder.
    Priority 1: Session-aware data from live AI interview (Highest accuracy)
    Priority 2: Resume-based keyword parsing (Fallback)
    Priority 3: No-data generic fallback
    """

    # Make sure lists are safely initialized
    skills = skills or []
    strengths = strengths or []
    gaps = gaps or []

    # ==========================================================
    #  PRIORITY 1: LIVE INTERVIEW SESSION DATA
    # ==========================================================
    # If the frontend passed a role and actual assessment gaps/strengths, use them!
    if role and (strengths or gaps or skills):
        return {
            "role": role.lower(),
            "skills": skills if skills else strengths, # Use strengths as baseline skills
            "strengths": strengths,
            "gaps": gaps, # The AI Generator needs these to create the roadmap!
            "language": language,
            "experience_level": "assessed_candidate" 
        }

    # ==========================================================
    #  PRIORITY 2: RESUME KEYWORD PARSING
    # ==========================================================
    text = (resume_text or "").lower()

    if "electrician" in text:
        return {
            "role": "electrician",
            "skills": ["wiring", "circuits", "safety"],
            "language": language,
            "experience_level": "intermediate"
        }

    elif "carpenter" in text:
        return {
            "role": "carpenter",
            "skills": ["cutting", "measurement", "tools"],
            "language": language,
            "experience_level": "beginner"
        }

    elif "mechanic" in text:
        return {
            "role": "mechanic",
            "skills": ["engine repair", "tools", "maintenance"],
            "language": language,
            "experience_level": "intermediate"
        }

    elif "plumber" in text:
        return {
            "role": "plumber",
            "skills": ["pipes", "fittings", "leak fixing"],
            "language": language,
            "experience_level": "beginner"
        }

    elif "developer" in text or "software" in text:
        return {
            "role": "developer",
            "skills": ["arrays", "c++"],
            "language": language,
            "experience_level": "beginner"
        }

    # ==========================================================
    #  PRIORITY 3: NO DATA (GENERAL FALLBACK)
    # ==========================================================
    return {
        "role": "general_worker",
        "skills": ["basic work"],
        "language": language,
        "experience_level": "beginner"
    }