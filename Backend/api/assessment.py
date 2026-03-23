from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import time
import base64

from AI_Service.src.engine.interview_manager import InterviewManager
from AI_Service.src.engine.interview_workflow import orchestrate_interview_turn
from AI_Service.src.engine.translator import translate_to_english, translate_to_user_language
from AI_Service.src.stt.transcriber import transcribe_audio
from AI_Service.src.tts.generator import generate_speech

from services.db import skills_collection


router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

manager = InterviewManager()

TEMP_DIR = "temp_data"
os.makedirs(TEMP_DIR, exist_ok=True)


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
    except Exception:
        audio_base64 = None

    return JSONResponse({
        "session_id": session.session_id,
        "question": localized_question,
        "audio": audio_base64,
    })


@router.post("/assess-voice")
async def process_voice_assessment(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
):
    temp_input_path = f"{TEMP_DIR}/incoming_{int(time.time())}_{audio.filename}"

    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        session = manager.get_session(session_id)
        prompt = manager.get_current_prompt(session)
        question = prompt["question"]
        user_lang = session.language

        user_text = transcribe_audio(temp_input_path, language="en")
        english_user_text = (
            user_text if user_lang.lower().startswith("en")
            else translate_to_english(user_text, user_lang)
        )

        chat_history = [
            {"question": t.question_text, "answer_en": t.answer_en}
            for t in session.history
        ]
        turn_result = orchestrate_interview_turn(
            manager=manager,
            session=session,
            prompt=prompt,
            question=question,
            answer_en=english_user_text,
            chat_history=chat_history,
        )

        response_text_en = str(turn_result["response_text"])
        if user_lang.lower().startswith("en"):
            response_text = response_text_en
        else:
            try:
                response_text = translate_to_user_language(response_text_en, user_lang)
            except Exception:
                response_text = response_text_en

        if turn_result["completed"]:
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
                    "badges": ["AI Verified"],
                }
                print("SAVING:", skill_data)
                skills_collection.insert_one(skill_data)
            except Exception as e:
                print("DB ERROR:", str(e))

            return JSONResponse({
                "interviewer_text": response_text,
                "audio": None,
            })

        try:
            audio_path = generate_speech(response_text, user_lang)
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
        except Exception:
            audio_base64 = None

        return JSONResponse({
            "interviewer_text": response_text,
            "audio": audio_base64,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/summary")
def get_summary(session_id: str):
    session = manager.get_session(session_id)
    return manager.summarize(session)


@router.post("/save-result")
def save_result(data: dict):
    try:
        skill_data = {
            "user_id": data.get("user_id"),
            "name": data.get("skill"),
            "trust": data.get("score"),
            "hours": 2,
            "status": "Verified" if data.get("score", 0) > 70 else "Learning",
            "badges": ["AI Verified"],
        }

        print("MANUAL SAVE:", skill_data)
        skills_collection.insert_one(skill_data)
        return {"success": True}
    except Exception as e:
        print("SAVE ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Save failed")