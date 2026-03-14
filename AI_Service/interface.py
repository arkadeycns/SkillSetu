import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.engine.counter_generator import generate_counter_questions
from src.engine.interview_manager import InterviewManager
from src.engine.question_bank import list_categories, reload_question_bank
from src.engine.translator import translate_to_english, translate_to_user_language
from src.rag.indexer import index_sops_from_file
from src.rag.retriever import retrieve_sops
from src.stt.transcriber import transcribe_audio
from src.tts.generator import generate_audio_response
from src.vision.analyzer import evaluate_competency

app = FastAPI()
manager = InterviewManager()


def _safe_suffix(filename: str, default_suffix: str) -> str:
    suffix = Path(filename or "").suffix
    return suffix if suffix else default_suffix


def _remove_file(path: str) -> None:
    if path and os.path.exists(path):
        os.remove(path)


def _to_audio_file(localized_feedback: str, user_lang: str, request_id: str) -> str | None:
    if not localized_feedback:
        return None
    output_audio_path = f"data/{request_id}_feedback.mp3"
    generate_audio_response(localized_feedback, user_lang, output_filename=output_audio_path)
    return Path(output_audio_path).name


def _question_bank_save_path(filename: str) -> str:
    safe_name = os.path.basename(filename or "question_bank.custom.json")
    if not safe_name.endswith(".json"):
        safe_name += ".json"
    return os.path.join("data", f"{uuid4().hex}_{safe_name}")


def _sop_save_path(filename: str) -> str:
    safe_name = os.path.basename(filename or "sop.txt")
    if not safe_name.endswith(".txt"):
        safe_name += ".txt"
    return os.path.join("data", f"{uuid4().hex}_{safe_name}")


@app.get("/api/assessment/categories")
def get_assessment_categories():
    try:
        return {"categories": list_categories()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to load categories: {exc}") from exc


@app.post("/api/assessment/start")
def start_assessment(category_id: str = Form(...)):
    try:
        session = manager.start_session(category_id=category_id)
        prompt = manager.get_current_prompt(session)
        return {
            "session_id": session.session_id,
            "category_id": session.category_id,
            "next_prompt": prompt,
            "message": "Assessment started. Answer this primary question.",
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/admin/questions/upload")
async def upload_custom_question_bank(question_bank_file: UploadFile = File(...)):
    os.makedirs("data", exist_ok=True)
    target_path = _question_bank_save_path(question_bank_file.filename)

    with open(target_path, "wb") as handle:
        shutil.copyfileobj(question_bank_file.file, handle)

    try:
        active_path = reload_question_bank(path=target_path)
        return {
            "message": "Question bank uploaded and activated.",
            "active_question_bank_path": active_path,
            "categories": list_categories(),
        }
    except Exception as exc:
        _remove_file(target_path)
        raise HTTPException(status_code=400, detail=f"Invalid question bank file: {exc}") from exc


@app.post("/api/admin/questions/reload")
def reload_questions_from_path(path: str = Form(...)):
    try:
        active_path = reload_question_bank(path=path)
        return {
            "message": "Question bank reloaded.",
            "active_question_bank_path": active_path,
            "categories": list_categories(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to reload question bank: {exc}") from exc


@app.post("/api/admin/sops/index")
async def upload_and_index_sops(sop_file: UploadFile = File(...), batch_size: int = Form(25)):
    os.makedirs("data", exist_ok=True)
    sop_path = _sop_save_path(sop_file.filename)

    with open(sop_path, "wb") as handle:
        shutil.copyfileobj(sop_file.file, handle)

    try:
        result = index_sops_from_file(file_path=sop_path, batch_size=batch_size)
        return {
            "message": "SOP indexed successfully.",
            "source_file": os.path.basename(sop_path),
            "index_name": "skillsetu-sops",
            "chunks": result["chunks"],
            "upserted": result["upserted"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"SOP indexing failed: {exc}") from exc
    finally:
        _remove_file(sop_path)


@app.get("/api/assessment/{session_id}/next")
def get_next_prompt(session_id: str):
    try:
        session = manager.get_session(session_id)
        return {
            "session_id": session.session_id,
            "category_id": session.category_id,
            "next_prompt": manager.get_current_prompt(session),
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/assessment/{session_id}/answer")
async def submit_assessment_answer(
    session_id: str,
    audio: UploadFile = File(...),
    image: UploadFile = File(...),
):
    os.makedirs("data", exist_ok=True)
    request_id = uuid4().hex
    temp_audio_path = f"data/{request_id}_input{_safe_suffix(audio.filename, '.wav')}"
    temp_image_path = f"data/{request_id}_image{_safe_suffix(image.filename, '.jpg')}"

    with open(temp_audio_path, "wb") as audio_buffer:
        shutil.copyfileobj(audio.file, audio_buffer)
    with open(temp_image_path, "wb") as image_buffer:
        shutil.copyfileobj(image.file, image_buffer)

    try:
        session = manager.get_session(session_id)
        prompt = manager.get_current_prompt(session)
        if prompt["stage"] == "completed":
            raise HTTPException(status_code=400, detail="Assessment already completed for this session.")

        original_text, user_lang = transcribe_audio(temp_audio_path)
        english_text = translate_to_english(original_text, user_lang)

        retrieval_query = (
            f"Category: {session.category_id}\n"
            f"Question: {prompt['question']}\n"
            f"Candidate answer: {english_text}\n"
            f"Stage: {prompt['stage']}"
        )
        sop_context = retrieve_sops(retrieval_query, top_k=4)

        evaluation = evaluate_competency(
            image_path=temp_image_path,
            user_transcript=english_text,
            sop_context=sop_context,
        )
        manager.record_answer(session, answer_en=english_text, evaluation=evaluation)

        if prompt["stage"] == "primary":
            counters = generate_counter_questions(
                primary_question=prompt["question"],
                user_answer_en=english_text,
                identified_gaps=evaluation.get("identified_gaps", []),
                sop_context=sop_context,
                count=2,
                previous_questions=[],
            )
            manager.advance_after_primary(session, counters=counters)
        else:
            manager.advance_after_counter(session)

        next_prompt = manager.get_current_prompt(session)
        feedback_en = str(evaluation.get("feedback", "")).strip()
        localized_feedback = translate_to_user_language(feedback_en, user_lang) if feedback_en else ""
        feedback_audio_file = _to_audio_file(localized_feedback, user_lang, request_id)

        return {
            "session_id": session.session_id,
            "category_id": session.category_id,
            "answered_stage": prompt["stage"],
            "detected_language": user_lang,
            "transcript_original": original_text,
            "transcript_english": english_text,
            "evaluation": evaluation,
            "localized_feedback": localized_feedback,
            "feedback_audio_file": feedback_audio_file,
            "next_prompt": next_prompt,
            "is_completed": next_prompt["stage"] == "completed",
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Assessment pipeline failed: {exc}") from exc
    finally:
        _remove_file(temp_audio_path)
        _remove_file(temp_image_path)


@app.get("/api/assessment/{session_id}/summary")
def get_assessment_summary(session_id: str):
    try:
        session = manager.get_session(session_id)
        return manager.summarize(session)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/assessment/audio/{filename}")
def get_feedback_audio(filename: str):
    safe_name = os.path.basename(filename)
    if safe_name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    path = os.path.join("data", safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found.")

    return FileResponse(path, media_type="audio/mpeg", filename=safe_name)