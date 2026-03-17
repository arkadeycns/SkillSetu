from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import time
import base64

# Interview engine
from AI_Service.src.engine.interview_manager import InterviewManager
from AI_Service.src.engine.interview_workflow import decide_turn_outcome, generate_counters_for_primary
from AI_Service.src.engine.question_bank import list_categories

# NLP utilities
from AI_Service.src.engine.translator import translate_to_english, translate_to_user_language

# AI modules
from AI_Service.src.stt.transcriber import transcribe_audio

from AI_Service.src.rag.qa import rag_query
from services.tts_service import generate_speech

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

manager = InterviewManager()

TEMP_DIR = "temp_data"
os.makedirs(TEMP_DIR, exist_ok=True)


# ==========================================================
# START SESSION
# ==========================================================

@router.post("/start-session")
def start_session(skill: str = Form(...), language: str = Form(...)):

    try:

        session = manager.start_session(category_id=skill)
        session.language = language

        prompt = manager.get_current_prompt(session)
        question_en = prompt["question"]

        if language.lower().startswith("en"):
            localized_question = question_en
        else:
            localized_question = translate_to_user_language(question_en, language)

        audio_path = generate_speech(localized_question, language)

        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()

        return JSONResponse({
            "session_id": session.session_id,
            "question": localized_question,
            "audio": audio_base64
        })

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# VOICE INTERVIEW LOOP
# ==========================================================

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

        whisper_lang_map = {
            "english": "en",
            "hindi": "hi",
            "hinglish": "hi",
            "tamil": "ta",
            "telugu": "te",
            "bengali": "bn"
        }

        stt_lang_code = whisper_lang_map.get(user_lang.lower(), "en")

        # ===============================
        # SPEECH TO TEXT
        # ===============================

        user_text = transcribe_audio(temp_input_path, language=stt_lang_code)

        print("User speech:", user_text)

        if user_lang.lower().startswith("en"):
            english_user_text = user_text
        else:
            english_user_text = translate_to_english(user_text, user_lang)

        print("Translated answer:", english_user_text)

        # ===============================
        # RAG FEEDBACK
        # ===============================

        chat_history = [
            {"question": turn.question_text, "answer_en": turn.answer_en}
            for turn in getattr(session, "history", [])
        ]

        outcome = decide_turn_outcome(
            question=question,
            answer_en=english_user_text,
            stage=prompt["stage"],
            retry_used=getattr(session, "retry_used_for_primary", False),
            counter_retry_used=getattr(session, "counter_retry_used_for_current", False),
            chat_history=chat_history,
        )

        if outcome.get("use_qa_feedback", True):
            ai_feedback_en = rag_query(
                question,
                english_user_text,
                chat_history=chat_history
            )
        else:
            ai_feedback_en = outcome.get("feedback", "")

        print("RAG output:", ai_feedback_en)

        next_step = outcome.get("next_step", "advance")

        if prompt["stage"] in {"primary", "retry_primary"}:
            if next_step == "retry_primary" and prompt["stage"] == "primary":
                manager.advance_after_unsatisfactory_primary(session)
            elif next_step == "ask_counter":
                previous_counter_questions = [
                    turn.question_text
                    for turn in getattr(session, "history", [])
                    if str(turn.stage).startswith("counter_")
                ]
                counters = generate_counters_for_primary(
                    primary_question=question,
                    answer_en=english_user_text,
                    feedback=ai_feedback_en,
                    previous_questions=previous_counter_questions,
                    count=2,
                )
                manager.advance_after_primary(session, counters=counters)
            else:
                manager.skip_current_primary(session)
        else:
            if next_step == "retry_counter":
                if not manager.retry_current_counter(session):
                    manager.advance_after_counter(session)
            else:
                manager.advance_after_counter(session)

        print("Turn outcome:", outcome)

        manager.record_answer(
            session,
            answer_en=english_user_text,
            evaluation={
                "feedback": ai_feedback_en,
                "next_step": outcome.get("next_step", "advance"),
            },
        )

        next_prompt = manager.get_current_prompt(session)
        if next_prompt["stage"] == "completed":
            interviewer_text_en = "Assessment complete. Tap End to view your final report."
        else:
            feedback_en = ai_feedback_en or outcome.get("feedback", "")
            next_q = next_prompt["question"]
            is_retry_turn = (
                outcome.get("next_step") in {"retry_primary", "retry_counter"}
                or next_q.strip() == question.strip()
            )
            if is_retry_turn:
                interviewer_text_en = (
                    f"{feedback_en} This is a retry. Please answer this question again: {next_q}"
                    if feedback_en
                    else f"This is a retry. Please answer this question again: {next_q}"
                )
            else:
                interviewer_text_en = f"{feedback_en} Next question: {next_q}" if feedback_en else next_q

        if user_lang.lower().startswith("en"):
            interviewer_text_local = interviewer_text_en
            feedback_local = outcome.get("feedback", "")
        else:
            interviewer_text_local = translate_to_user_language(interviewer_text_en, user_lang)
            feedback_local = translate_to_user_language(outcome.get("feedback", ""), user_lang)

        print("Interviewer response:", interviewer_text_local)

        # ===============================
        # TEXT TO SPEECH
        # ===============================

        audio_path = generate_speech(interviewer_text_local, user_lang)

        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        return JSONResponse({
            "interviewer_text": interviewer_text_local,
            "feedback": feedback_local,
            "audio": audio_base64
        })

    except Exception as exc:

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# GET CATEGORIES
# ==========================================================

@router.get("/categories")
def get_assessment_categories():

    try:
        categories = list_categories()
        return {"categories": categories}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# SESSION SUMMARY
# ==========================================================

@router.get("/{session_id}/summary")
def get_summary(session_id: str):

    try:

        session = manager.get_session(session_id)
        return manager.summarize(session)

    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))