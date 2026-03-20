from fastapi import APIRouter, UploadFile, File, Form
import os
import shutil
import time
import base64

from services.data_provider import get_user_resume_data
from services.ai_engine import generate_chat_response
from AI_Service.src.stt.transcriber import transcribe_audio
from services.tts_service import generate_speech

router = APIRouter(prefix="/api/chat", tags=["Chat"])

#  In-memory session storage (replace with Redis/DB later)
sessions = {}

TEMP_DIR = "temp_chat_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post("/")
async def chat(
    message: str = Form(None),
    session_id: str = Form("default"),
    user_id: str = Form(None),
    resume_text: str = Form(None),   
    audio: UploadFile = File(None),
    language: str = Form("en")
):
    try:
        # ==========================================================
        #  AUDIO → TEXT
        # ==========================================================
        if audio:
            temp_path = f"{TEMP_DIR}/audio_{int(time.time())}_{audio.filename}"

            try:
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(audio.file, buffer)

                message = transcribe_audio(temp_path, language=language)

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # ==========================================================
        #  VALIDATION
        # ==========================================================
        if not message or not message.strip():
            return {"success": False, "error": "No message provided"}

        # ==========================================================
        # SESSION HISTORY (LIMITED CONTEXT)
        # ==========================================================
        history = sessions.get(session_id, [])
        history = history[-5:]  # keep last 5 turns

        # ==========================================================
        #  USER DATA (NO HARDCODING)
        # ==========================================================
        user_data = get_user_resume_data(
            user_id=user_id,
            resume_text=resume_text
        )

        # ==========================================================
        #  AI RESPONSE
        # ==========================================================
        reply = generate_chat_response(message, user_data, history)

        # ==========================================================
        #  STORE HISTORY (RAG FORMAT)
        # ==========================================================
        history.append({
            "question": message,
            "answer_en": reply
        })
        sessions[session_id] = history

        # ==========================================================
        # TEXT → AUDIO
        # ==========================================================
        audio_base64 = None
        try:
            audio_path = generate_speech(reply, language)

            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()

        except Exception as e:
            print(" TTS FAILED:", e)

        # ==========================================================
        #  FINAL RESPONSE
        # ==========================================================
        return {
            "success": True,
            "reply": reply,
            "audio": audio_base64,
            "session_id": session_id
        }

    except Exception as e:
        print(" CHAT ERROR:", e)
        return {
            "success": False,
            "error": "Internal server error"
        }