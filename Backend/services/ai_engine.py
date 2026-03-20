from AI_Service.src.rag.qa import rag_query
import threading
import json
import re


# ==========================================================
#  SAFE RAG CALL (WITH TIMEOUT)
# ==========================================================

def _safe_rag_query(result_container, question, user_answer, history):
    try:
        response = rag_query(
            question=question,
            user_answer=user_answer,
            chat_history=history
        )
        result_container["response"] = response

    except Exception as e:
        result_container["error"] = str(e)


# ==========================================================
#  CHAT ENGINE
# ==========================================================

def generate_chat_response(message, user_data, history):

    skills = user_data.get("skills", [])
    experience = user_data.get("experience_level", "unknown")
    resume_text = user_data.get("resume_text", "")

    context = f"""
You are a helpful career guide for blue-collar workers.

User Info:
- Resume: {resume_text}
- Skills: {skills}
- Experience Level: {experience}

User Question:
{message}

Instructions:
- Understand user's job from context
- Do NOT assume software field unless mentioned
- Use simple language
- Give step-by-step practical guidance
"""

    result_container = {}

    thread = threading.Thread(
        target=_safe_rag_query,
        args=(result_container, context, message, history)
    )

    thread.start()
    thread.join(timeout=8)

    if thread.is_alive():
        return "It is taking too long to respond. Please try again."

    if "error" in result_container:
        print("RAG ERROR:", result_container["error"])
        return "I could not process your request. Please try again."

    return result_container.get(
        "response",
        "I will help you step by step. Please ask again."
    )


# ==========================================================
#  GREETING GENERATION
# ==========================================================

def generate_greeting(user_data, language="en"):

    skills = user_data.get("skills", [])
    experience = user_data.get("experience_level", "unknown")

    prompt = f"""
You are a friendly career coach.

User Info:
- Skills: {skills}
- Experience: {experience}

Task:
Generate a SHORT welcoming greeting.

Rules:
- Max 2 sentences
- Friendly and motivating
- Simple language
- Personalize using their skills if possible
- No extra explanation
"""

    result_container = {}

    thread = threading.Thread(
        target=_safe_rag_query,
        args=(result_container, prompt, "", [])
    )

    thread.start()
    thread.join(timeout=6)

    if thread.is_alive():
        return "Hello! I am here to guide you."

    if "error" in result_container:
        return "Hello! Let’s get started."

    return result_container.get("response", "Hello! Let’s begin.")


# ==========================================================
#  ROADMAP GENERATION
# ==========================================================

def generate_roadmap(user_data):

    skills = user_data.get("skills", [])
    experience = user_data.get("experience_level", "unknown")
    resume_text = user_data.get("resume_text", "")

    prompt = f"""
You are a career mentor.

User Info:
- Resume: {resume_text}
- Skills: {skills}
- Experience: {experience}

Your task:
1. Identify user's profession
2. Suggest skills to learn next
3. Provide timeline
4. Suggest practical projects

IMPORTANT:
- Focus on real-world roles (electrician, carpenter, mechanic, etc.)
- Do NOT assume software role unless mentioned
- Keep language simple
"""

    result_container = {}

    thread = threading.Thread(
        target=_safe_rag_query,
        args=(result_container, prompt, "", [])
    )

    thread.start()
    thread.join(timeout=10)

    if thread.is_alive():
        return {"error": "Roadmap generation timed out"}

    if "error" in result_container:
        return {"error": result_container["error"]}

    return result_container.get("response", {})


# ==========================================================
#  TRAINING RECOMMENDATIONS (STRICT JSON + SAFE PARSE)
# ==========================================================

def generate_training_recommendations(user_data):

    skills = user_data.get("skills", [])
    experience = user_data.get("experience_level", "unknown")
    resume_text = user_data.get("resume_text", "")

    prompt = f"""
You are a career mentor for blue-collar workers.

User Info:
- Resume: {resume_text}
- Current Skills: {skills}
- Experience: {experience}

Your task:
Return STRICT JSON ONLY.

Format:
[
  {{
    "module": "string",
    "skills_to_learn": ["skill1", "skill2"],
    "duration": "string",
    "practice_task": "string"
  }}
]

Rules:
- Output MUST be valid JSON
- NO text outside JSON
- Minimum 3 modules
- Focus on practical skills
- Do NOT assume software field unless mentioned
"""

    result_container = {}

    thread = threading.Thread(
        target=_safe_rag_query,
        args=(result_container, prompt, "", [])
    )

    thread.start()
    thread.join(timeout=10)

    if thread.is_alive():
        return {"modules": []}

    if "error" in result_container:
        return {"modules": []}

    raw_response = result_container.get("response", "")

    # ==========================================================
    #  SAFE JSON EXTRACTION 
    # ==========================================================
    try:
        json_match = re.search(r"\[.*\]", raw_response, re.DOTALL)

        if json_match:
            parsed = json.loads(json_match.group())
            if isinstance(parsed, list):
                return {"modules": parsed}

        return {"modules": []}

    except Exception:
        print("JSON PARSE ERROR:", raw_response)
        return {"modules": []}