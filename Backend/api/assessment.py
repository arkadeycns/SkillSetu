from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import time
import base64
from typing import List

# Interview engine
from AI_Service.src.engine.interview_manager import InterviewManager
from AI_Service.src.engine.interview_workflow import decide_turn_outcome, generate_counters_for_primary
from AI_Service.src.engine.question_bank import list_categories

# NLP utilities
from AI_Service.src.engine.translator import translate_to_english, translate_to_user_language

# AI modules
from AI_Service.src.stt.transcriber import transcribe_audio
from AI_Service.src.rag.qa import rag_query
from AI_Service.src.tts.generator import generate_speech
from AI_Service.src.engine.ai_engine import generate_training_recommendations

from services.data_provider import get_user_resume_data
from services.db import skills_collection   # ✅ ADDED

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

manager = InterviewManager()

TEMP_DIR = "temp_data"
os.makedirs(TEMP_DIR, exist_ok=True)


def _expected_skills_for_category(category_id: str, user_data: dict) -> List[str]:
    category_lookup = {
        item.get("id", "").lower(): item.get("title", "").lower()
        for item in list_categories()
    }
    title = category_lookup.get((category_id or "").lower(), "")
    text = f"{(category_id or '').lower()} {title}".strip()

    if any(key in text for key in ["electric", "wire"]):
        return ["wiring", "circuit safety", "fault diagnosis", "tool handling"]
    if any(key in text for key in ["carpent", "wood"]):
        return ["measurement", "cutting", "joinery", "tool safety"]
    if any(key in text for key in ["plumb", "pipe"]):
        return ["pipe fitting", "leak diagnosis", "joint sealing", "safety"]
    if any(key in text for key in ["mechanic", "automotive", "engine"]):
        return ["inspection", "troubleshooting", "preventive maintenance", "tool safety"]
    if any(key in text for key in ["mern", "developer", "software"]):
        return ["problem solving", "api usage", "debugging", "version control"]

    user_skills = [str(skill).strip() for skill in user_data.get("skills", []) if str(skill).strip()]
    return user_skills if user_skills else ["core fundamentals"]


# =========================
# START SESSION
# =========================
@router.post("/start-session")
def start_session(skill: str = Form(...), language: str = Form(...)):

    session = manager.start_session(category_id=skill)
    session.language = language

    prompt = manager.get_current_prompt(session)
    question_en = prompt["question"]

    localized_question = (
        question_en if language.lower().startswith("en")
        else translate_to_user_language(question_en, language)
    )

    try:
        audio_path = generate_speech(localized_question, language)
        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
    except:
        audio_base64 = None

    return JSONResponse({
        "session_id": session.session_id,
        "question": localized_question,
        "audio": audio_base64
    })


# =========================
# VOICE LOOP
# =========================
@router.post("/assess-voice")
async def process_voice_assessment(
    audio: UploadFile = File(...),
    session_id: str = Form(...)
):

    temp_input_path = f"{TEMP_DIR}/incoming_{int(time.time())}_{audio.filename}"

    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        session = manager.get_session(session_id)
        prompt = manager.get_current_prompt(session)
        question = prompt["question"]

        user_lang = session.language

        # =========================
        # SPEECH → TEXT
        # =========================
        user_text = transcribe_audio(temp_input_path, language="en")

        english_user_text = (
            user_text if user_lang.lower().startswith("en")
            else translate_to_english(user_text, user_lang)
        )

        # =========================
        # DECISION
        # =========================
        chat_history = [
            {"question": t.question_text, "answer_en": t.answer_en}
            for t in session.history
        ]

        outcome = decide_turn_outcome(
            question=question,
            answer_en=english_user_text,
            stage=prompt["stage"],
            retry_used=session.retry_used_for_primary,
            counter_retry_used=session.counter_retry_used_for_current,
            chat_history=chat_history,
        )

        ai_feedback_en = rag_query(question, english_user_text)

        next_step = outcome.get("next_step", "advance")

        # =========================
        # FLOW CONTROL
        # =========================
        if prompt["stage"] in {"primary", "retry_primary"}:
            if next_step == "retry_primary":
                manager.advance_after_unsatisfactory_primary(session)
            elif next_step == "ask_counter":
                counters = generate_counters_for_primary(
                    question, english_user_text, ai_feedback_en, [], 2
                )
                manager.advance_after_primary(session, counters)
            else:
                manager.skip_current_primary(session)
        else:
            manager.advance_after_counter(session)

        manager.record_answer(
            session,
            answer_en=english_user_text,
            evaluation={"feedback": ai_feedback_en}
        )

        next_prompt = manager.get_current_prompt(session)

        # =========================
        # ✅ SAVE TO DB WHEN DONE
        # =========================
        if next_prompt["stage"] == "completed":
            try:
                summary = manager.summarize(session)

                trust = summary.get("overall_score", 0)
                hours = round(len(session.history) * 0.1, 1)

                skill_data = {
                    "user_id": "test_user_123",
                    "name": session.category_id,
                    "trust": trust,
                    "hours": hours,
                    "status": "Verified" if trust > 70 else "Learning",
                    "badges": ["AI Verified"]
                }

                print("🔥 SAVING:", skill_data)
                skills_collection.insert_one(skill_data)

            except Exception as e:
                print("❌ DB ERROR:", str(e))

            return JSONResponse({
                "interviewer_text": "Assessment completed",
                "audio": None
            })

        # =========================
        # NEXT QUESTION
        # =========================
        next_q = next_prompt["question"]
        response_text = f"{ai_feedback_en} Next question: {next_q}"

        try:
            audio_path = generate_speech(response_text, user_lang)
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
        except:
            audio_base64 = None

        return JSONResponse({
            "interviewer_text": response_text,
            "audio": audio_base64
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# SUMMARY
# =========================
@router.get("/{session_id}/summary")
def get_summary(session_id: str):
    session = manager.get_session(session_id)
    return manager.summarize(session)

@router.post("/save-result")
def save_result(data: dict):
    try:
        from services.db import skills_collection

        skill_data = {
            "user_id": data.get("user_id"),
            "name": data.get("skill"),   # wallet expects 'name'
            "trust": data.get("score"),  # wallet expects 'trust'
            "hours": 2,  # you can improve later
            "status": "Verified" if data.get("score", 0) > 70 else "Learning",
            "badges": ["AI Verified"]
        }

        print("🔥 MANUAL SAVE:", skill_data)

        skills_collection.insert_one(skill_data)

        return {"success": True}

    except Exception as e:
        print("❌ SAVE ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Save failed")