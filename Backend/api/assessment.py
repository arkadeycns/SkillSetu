from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
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

        chat_history = getattr(session, "answers", [])

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

        # ===============================
        # GENERATE COUNTER QUESTION
        # ===============================

        if prompt["stage"] == "primary":

            counters = generate_counter_questions(
                primary_question=question,
                user_answer_en=english_user_text,
                identified_gaps=ai_feedback_en,
                sop_context=ai_feedback_en,
                count=1,
                previous_questions=chat_history
            )

            # Safe fallback if generator fails
            if counters and len(counters) > 0:
                counter_question = counters[0]
            else:
                counter_question = "Can you explain your answer in more detail?"

            manager.advance_after_primary(session, counters=counters)

        else:

            manager.advance_after_counter(session)

            next_prompt = manager.get_current_prompt(session)
            counter_question = next_prompt["question"]

        print("Counter question:", counter_question)

        # ===============================
        # COMBINE FEEDBACK + COUNTER
        # ===============================

        combined_text_en = f"{ai_feedback_en}. Now tell me this: {counter_question}"

        if user_lang.lower().startswith("en"):
            combined_text_local = combined_text_en
        else:
            combined_text_local = translate_to_user_language(combined_text_en, user_lang)

        print("Interviewer response:", combined_text_local)

        # ===============================
        # TEXT TO SPEECH
        # ===============================

        audio_path = generate_speech(combined_text_local, user_lang)

        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        return JSONResponse({
            "interviewer_text": combined_text_local,
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