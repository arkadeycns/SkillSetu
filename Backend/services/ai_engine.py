from AI_Service.src.rag.qa import rag_query
import threading


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
#  CHAT ENGINE (IMPROVED - NO HARDCODING)
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
#  ROADMAP GENERATION (IMPROVED - NO HARDCODING)
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
#  TRAINING RECOMMENDATIONS (FIXED - NO HARDCODING)
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
1. Identify user's job role
2. Identify missing skills
3. Suggest learning order
4. Provide simple practice plan

IMPORTANT:
- Do NOT assume software field unless explicitly mentioned
- Focus on practical real-world skills
- Keep response simple
"""

    result_container = {}

    thread = threading.Thread(
        target=_safe_rag_query,
        args=(result_container, prompt, "", [])
    )

    thread.start()
    thread.join(timeout=10)

    if thread.is_alive():
        return {
            "plan": "Taking too long. Please try again."
        }

    if "error" in result_container:
        return {
            "plan": "Error generating recommendations"
        }

    return {
        "plan": result_container.get("response", "")
    }