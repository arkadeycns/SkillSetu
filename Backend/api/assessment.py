from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import shutil
import time
from uuid import uuid4

# Interview engine
from AI_Service.src.engine.interview_manager import InterviewManager
from AI_Service.src.engine.counter_generator import generate_counter_questions
from AI_Service.src.engine.question_bank import list_categories

# NLP utilities
from AI_Service.src.engine.translator import translate_to_english, translate_to_user_language

# AI modules
from AI_Service.src.vision.analyzer import evaluate_competency
from AI_Service.src.stt.transcriber import transcribe_audio
from AI_Service.src.rag.retriever import retrieve_sops

from services.rag_service import rag_query
from services.tts_service import generate_speech
from services.bootstrap_service import get_next_assessment_question

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

manager = InterviewManager()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def remove_temp_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as exc:
            print(f"Cleanup error: {exc}")


@router.post("/assess-voice")
async def process_voice_assessment(
    audio: UploadFile = File(...),
    question: str | None = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    os.makedirs("temp_data", exist_ok=True)
    os.makedirs("audio", exist_ok=True)

    temp_input_path = f"temp_data/incoming_{int(time.time())}_{audio.filename}"

    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    resolved_question = (question or "").strip()
    if not resolved_question:
        resolved_question = get_next_assessment_question()

    try:
        stt_result = transcribe_audio(temp_input_path)
        if isinstance(stt_result, tuple):
            user_text = stt_result[0]
            user_lang = stt_result[1] if len(stt_result) > 1 else "en"
        else:
            user_text = stt_result
            user_lang = "en"
        print(f"STT Output: {user_text}")

        english_user_text = translate_to_english(user_text, user_lang) if user_text else ""

        ai_feedback_en = rag_query(resolved_question, english_user_text)
        print(f"RAG Output (EN): {ai_feedback_en}")

        if (user_lang or "").lower().startswith("en"):
            ai_feedback_localized = ai_feedback_en
        else:
            ai_feedback_localized = translate_to_user_language(ai_feedback_en, user_lang)

        output_audio_path = generate_speech(ai_feedback_localized, user_lang)

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        background_tasks.add_task(remove_temp_file, output_audio_path)
        return FileResponse(output_audio_path, media_type="audio/mpeg")

    except Exception as exc:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        print(f"CRITICAL ERROR: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/categories")
def get_assessment_categories():
    try:
        categories = list_categories()
        return {"categories": categories}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/start")
def start_assessment(category_id: str = Form(...)):
    try:
        session = manager.start_session(category_id=category_id)
        prompt = manager.get_current_prompt(session)

        return {
            "session_id": session.session_id,
            "category_id": session.category_id,
            "next_prompt": prompt
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{session_id}/next")
def get_next_prompt(session_id: str):
    try:
        session = manager.get_session(session_id)
        prompt = manager.get_current_prompt(session)

        return {
            "session_id": session.session_id,
            "category_id": session.category_id,
            "next_prompt": prompt
        }

    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    audio: UploadFile = File(...),
    image: UploadFile = File(...)
):

    request_id = uuid4().hex

    audio_path = f"{DATA_DIR}/{request_id}_audio.wav"
    image_path = f"{DATA_DIR}/{request_id}_image.jpg"

    try:

        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        session = manager.get_session(session_id)
        prompt = manager.get_current_prompt(session)

        # Speech → Text
        original_text, user_lang = transcribe_audio(audio_path)

        # Translate to English
        english_text = translate_to_english(original_text, user_lang)

        # Build retrieval query
        retrieval_query = f"""
        Category: {session.category_id}
        Question: {prompt['question']}
        Candidate answer: {english_text}
        """

        # Retrieve SOP context
        sop_context = retrieve_sops(retrieval_query)

        # Evaluate competency
        evaluation = evaluate_competency(
            image_path=image_path,
            user_transcript=english_text,
            sop_context=sop_context
        )

        manager.record_answer(
            session,
            answer_en=english_text,
            evaluation=evaluation
        )

        if prompt["stage"] == "primary":

            counters = generate_counter_questions(
                primary_question=prompt["question"],
                user_answer_en=english_text,
                identified_gaps=evaluation.get("identified_gaps", []),
                sop_context=sop_context,
                count=2,
                previous_questions=[]
            )

            manager.advance_after_primary(session, counters=counters)

        else:
            manager.advance_after_counter(session)

        next_prompt = manager.get_current_prompt(session)

        return {
            "session_id": session.session_id,
            "transcript_original": original_text,
            "transcript_english": english_text,
            "evaluation": evaluation,
            "next_prompt": next_prompt
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

        if os.path.exists(image_path):
            os.remove(image_path)


@router.get("/{session_id}/summary")
def get_summary(session_id: str):

    try:
        session = manager.get_session(session_id)
        return manager.summarize(session)

    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
