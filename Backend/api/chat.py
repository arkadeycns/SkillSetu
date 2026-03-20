from fastapi import APIRouter
from services.data_provider import get_user_resume_data
from services.ai_engine import generate_chat_response

# Optional voice imports
try:
    from services.stt_service import speech_to_text
    from services.tts_service import text_to_speech
except:
    speech_to_text = None
    text_to_speech = None

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/")
async def chat(data: dict):
    try:
        user_id = data.get("user_id")
        message = data.get("message")
        resume_text = data.get("resume_text")
        audio = data.get("audio")  # optional

        # 🎤 Voice → Text
        if audio and speech_to_text:
            try:
                message = speech_to_text(audio)
            except Exception as e:
                print(" STT failed:", e)

        #  Ensure message exists
        if not message:
            return {
                "success": False,
                "error": "No message provided"
            }

        #  Get user context
        user_data = get_user_resume_data(
            user_id=user_id,
            resume_text=resume_text
        )

        #  Generate AI reply
        reply = generate_chat_response(message, user_data)

        # 🔊 Text → Speech (SAFE)
        audio_output = None
        if text_to_speech:
            try:
                audio_output = text_to_speech(reply)
            except Exception as e:
                print(" TTS failed:", e)

        return {
            "success": True,
            "reply": reply,
            "audio": audio_output
        }

    except Exception as e:
        print("🔥 CHAT ERROR:", e)
        return {
            "success": False,
            "error": str(e)
        }