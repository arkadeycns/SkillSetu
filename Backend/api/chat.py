from fastapi import APIRouter, UploadFile, File, Form
import os
import shutil
import time
import base64

from services.data_provider import get_user_resume_data
from AI_Service.src.engine.ai_engine import generate_chat_response, generate_greeting
from AI_Service.src.engine.translator import translate_to_english, translate_to_user_language
from AI_Service.src.stt.transcriber import transcribe_audio
from AI_Service.src.tts.generator import generate_speech

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# In-memory session storage
sessions = {}
session_meta = {}

TEMP_DIR = "temp_chat_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


def _start_fallback_greeting(language: str, selected_role: str | None) -> str:
    role_text = (selected_role or "your trade").replace("_", " ")
    lang = (language or "en").strip().lower()
    if lang in {"hindi", "hinglish", "hi", "hi-in"}:
        return f"Namaste. {role_text} role ke liye main aapko step-by-step guidance dunga. Aaj kis practical problem par kaam karna hai?"
    return f"Welcome. I will guide you step by step for {role_text}. What practical problem do you want to improve today?"


# ==========================================================
#  NORMAL CHAT
# ==========================================================
@router.post("")
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

        normalized_message = message
        if not language.lower().startswith("en"):
            try:
                normalized_message = translate_to_english(message, language)
            except Exception:
                normalized_message = message

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

        # Keep reasoning in English for parity with interviewer pipeline.
        reply_en = generate_chat_response(
            normalized_message,
            user_data,
            history,
            language="en",
            selected_role=selected_role,
        )

        if language.lower().startswith("en"):
            reply = reply_en
        else:
            try:
                reply = translate_to_user_language(reply_en, language)
            except Exception:
                reply = reply_en

        history.append({
            "question": normalized_message,
            "answer_en": reply_en
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

        existing_meta = session_meta.get(session_id, {})
        if (
            sessions.get(session_id) is not None
            and existing_meta.get("role") == selected_role
            and existing_meta.get("language") == language
            and existing_meta.get("greeting")
        ):
            greeting = str(existing_meta.get("greeting"))
        else:
            # Keep greeting reasoning in English, then localize for user language.
            greeting_en = generate_greeting(user_data, "en")
            if language.lower().startswith("en"):
                greeting = greeting_en
            else:
                try:
                    greeting = translate_to_user_language(greeting_en, language)
                except Exception:
                    greeting = greeting_en

            # reset session on fresh start for this session/role/language tuple
            sessions[session_id] = []
            session_meta[session_id] = {
                "role": selected_role,
                "language": language,
                "greeting": greeting,
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
        selected_role = skill or "your trade"
        greeting = _start_fallback_greeting(language, selected_role)
        session_meta[session_id] = {
            "role": selected_role,
            "language": language,
            "greeting": greeting,
        }
        if session_id not in sessions:
            sessions[session_id] = []
        return {
            "success": True,
            "greeting": greeting,
            "audio": None,
            "session_id": session_id,
        }