from fastapi import APIRouter, UploadFile, File, Form
import os
import shutil
import time
import base64

from services.data_provider import get_user_resume_data
from AI_Service.src.engine.ai_engine import generate_chat_response, generate_greeting
from AI_Service.src.stt.transcriber import transcribe_audio
from AI_Service.src.tts.generator import generate_speech

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# In-memory session storage
sessions = {}
session_meta = {}

TEMP_DIR = "temp_chat_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


# ==========================================================
#  NORMAL CHAT
# ==========================================================
@router.post("/")
async def chat(
    message: str = Form(None),
    session_id: str = Form("default"),
    user_id: str = Form(None),
    resume_text: str = Form(None),
    audio: UploadFile = File(None),
    skill: str = Form(None),
    language: str = Form("en")
):
    try:
        audio_lang = "hi" if language.lower() == "hinglish" else language

        # AUDIO → TEXT
        if audio:
            temp_path = f"{TEMP_DIR}/audio_{int(time.time())}_{audio.filename}"

            try:
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(audio.file, buffer)

                # Pass audio_lang instead of language
                message = transcribe_audio(temp_path, language=audio_lang)

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        if not message or not message.strip():
            return {"success": False, "error": "No message provided"}

        history = sessions.get(session_id, [])
        history = history[-5:]

        user_data = get_user_resume_data(
            user_id=user_id,
            resume_text=resume_text
        )

        selected_role = (
            skill
            or session_meta.get(session_id, {}).get("role")
            or user_data.get("role")
        )

        if selected_role:
            session_meta[session_id] = {
                "role": selected_role,
                "language": language,
            }

        # The Text AI still gets the original language setting inside the engine if needed
        reply = generate_chat_response(
            message,
            user_data,
            history,
            language=language,
            selected_role=selected_role,
        )

        history.append({
            "question": message,
            "answer_en": reply
        })
        sessions[session_id] = history

        audio_base64 = None
        try:
            # Pass audio_lang instead of language
            audio_path = generate_speech(reply, audio_lang)
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            print("TTS FAILED:", e)

        return {
            "success": True,
            "reply": reply,
            "audio": audio_base64,
            "session_id": session_id
        }

    except Exception as e:
        print("CHAT ERROR:", e)
        return {
            "success": False,
            "error": "Internal server error"
        }


# ==========================================================
#  NEW: START CHAT (GREETING)
# ==========================================================
@router.post("/start")
async def start_chat(
    session_id: str = Form("default"),
    user_id: str = Form(None),
    resume_text: str = Form(None),
    skill: str = Form(None),
    language: str = Form("en")
):
    try:
        audio_lang = "hi" if language.lower() == "hinglish" else language

        user_data = get_user_resume_data(
            user_id=user_id,
            resume_text=resume_text
        )

        selected_role = skill or user_data.get("role")
        if selected_role:
            user_data = {**user_data, "role": selected_role}

        # The Text AI still gets "Hinglish" so it writes in mixed language
        greeting = generate_greeting(user_data, language)

        # reset session (no pollution)
        sessions[session_id] = []
        session_meta[session_id] = {
            "role": selected_role,
            "language": language,
        }

        audio_base64 = None
        try:
            # Pass audio_lang instead of language
            audio_path = generate_speech(greeting, audio_lang)
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            print("TTS FAILED:", e)

        return {
            "success": True,
            "greeting": greeting,
            "audio": audio_base64,
            "session_id": session_id
        }

    except Exception as e:
        print("START CHAT ERROR:", e)
        return {
            "success": False,
            "error": "Failed to start chat"
        }