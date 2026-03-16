from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
import time
import base64

# Interview engine
from AI_Service.src.engine.interview_manager import InterviewManager
from AI_Service.src.engine.counter_generator import generate_counter_questions
from AI_Service.src.engine.question_bank import list_categories

# NLP utilities
from AI_Service.src.engine.translator import translate_to_english, translate_to_user_language

# AI modules
from AI_Service.src.stt.transcriber import transcribe_audio

from services.rag_service import rag_query
from services.tts_service import generate_speech

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

manager = InterviewManager()

DATA_DIR = "data"
TEMP_DIR = "temp_data"
AUDIO_DIR = "audio"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


def remove_temp_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as exc:
            print("Cleanup error:", exc)


# ==========================================================
# START SESSION
# ==========================================================

@router.post("/start-session")
def start_session(
    skill: str = Form(...),
    language: str = Form(...)
):

    print("\n==============================")
    print("START SESSION REQUEST RECEIVED")
    print("Skill:", skill)
    print("Language:", language)
    print("==============================")

    try:

        session = manager.start_session(category_id=skill)

        session.language = language

        print("Session created:", session.session_id)

        prompt = manager.get_current_prompt(session)
        question_en = prompt["question"]

        if language.lower().startswith("en"):
            localized_question = question_en
        else:
            localized_question = translate_to_user_language(question_en, language)

        print("Localized Question:", localized_question)

        print("Generating TTS audio...")
        audio_path = generate_speech(localized_question, session.language)

        print("Audio generated at:", audio_path)

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return JSONResponse({
            "session_id": session.session_id,
            "question": localized_question,
            "audio_base64": audio_base64
        })

    except Exception as exc:

        print("\n!!!!! START SESSION ERROR !!!!!")
        print(exc)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# VOICE INTERVIEW LOOP
# ==========================================================

@router.post("/assess-voice")
async def process_voice_assessment(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):

    print("\n==============================")
    print("VOICE ASSESSMENT REQUEST")
    print("Session ID:", session_id)
    print("==============================")

    temp_input_path = f"{TEMP_DIR}/incoming_{int(time.time())}_{audio.filename}"

    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:

        session = manager.get_session(session_id)
        print("Session loaded")

        prompt = manager.get_current_prompt(session)
        question = prompt["question"]

        print("Current question:", question)

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

        print(f"Running Speech-to-Text with mapped language code: {stt_lang_code} (Original: {user_lang})")

        user_text = transcribe_audio(temp_input_path, language=stt_lang_code)

        print("User speech:", user_text)

        if user_lang.lower().startswith("en"):
            english_user_text = user_text
        else:
            english_user_text = translate_to_english(user_text, user_lang)

        print("Translated answer:", english_user_text)

        # --------------------------------------------------
        # STATEFUL RAG
        # --------------------------------------------------

        chat_history = getattr(session, "answers", [])

        print("Running RAG query with session context...")

        ai_feedback_en = rag_query(
            question,
            english_user_text,
            chat_history=chat_history
        )

        print("RAG output:", ai_feedback_en)

        manager.record_answer(
            session,
            answer_en=english_user_text,
            evaluation={"feedback": ai_feedback_en}
        )

        # --------------------------------------------------
        # GENERATE FOLLOW-UP / COUNTER QUESTIONS
        # --------------------------------------------------

        if prompt["stage"] == "primary":

            counters = generate_counter_questions(
                primary_question=question,
                user_answer_en=english_user_text,
                identified_gaps=ai_feedback_en,
                sop_context=ai_feedback_en,
                count=2,
                previous_questions=chat_history
            )

            manager.advance_after_primary(session, counters=counters)

        else:
            manager.advance_after_counter(session)

        next_prompt = manager.get_current_prompt(session)
        next_question = next_prompt["question"]

        print("Next question:", next_question)

        if user_lang.lower().startswith("en"):
            localized_question = next_question
        else:
            localized_question = translate_to_user_language(next_question, user_lang)

        print("Localized next question:", localized_question)

        print("Generating next TTS audio...")

        output_audio_path = generate_speech(localized_question, session.language)

        background_tasks.add_task(remove_temp_file, output_audio_path)

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        print("Voice assessment completed\n")

        return FileResponse(output_audio_path, media_type="audio/mpeg")

    except Exception as exc:

        print("\n!!!!! VOICE ASSESSMENT ERROR !!!!!")
        print(exc)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# GET CATEGORIES
# ==========================================================

@router.get("/categories")
def get_assessment_categories():

    print("Fetching categories...")

    try:
        categories = list_categories()
        return {"categories": categories}

    except Exception as exc:

        print("CATEGORY FETCH ERROR:", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# SESSION SUMMARY
# ==========================================================

@router.get("/{session_id}/summary")
def get_summary(session_id: str):

    print("Summary requested for session:", session_id)

    try:

        session = manager.get_session(session_id)
        return manager.summarize(session)

    except Exception as exc:

        print("SUMMARY ERROR:", exc)
        raise HTTPException(status_code=404, detail=str(exc))