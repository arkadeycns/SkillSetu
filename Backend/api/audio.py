from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import time
import base64

#  STT 
from AI_Service.src.stt.transcriber import transcribe_audio

#  TTS 
from AI_Service.src.tts.generator import generate_speech

router = APIRouter(prefix="/api/audio", tags=["Audio"])

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


# ==========================================================
#  SPEECH TO TEXT + AI RESPONSE + TTS
# ==========================================================

@router.post("/process")
async def process_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="en")
):
    """
    Takes audio input → converts to text → returns transcript + audio response
    """

    temp_input_path = f"{TEMP_DIR}/audio_{int(time.time())}_{audio.filename}"

    try:
        
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # ===============================
        #  SPEECH TO TEXT
        # ===============================
        user_text = transcribe_audio(temp_input_path, language=language)

        # ===============================
        #  TEXT TO SPEECH (echo back)
        # ===============================
        audio_base64 = None
        try:
            audio_path = generate_speech(user_text, language)

            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()

        except Exception as e:
            print("TTS FAILED:", e)

        # ===============================
        #  CLEANUP
        # ===============================
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        return JSONResponse({
            "success": True,
            "transcript": user_text,
            "audio": audio_base64
        })

    except Exception as e:

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
#  TEXT TO SPEECH ONLY
# ==========================================================

@router.post("/tts")
async def text_to_audio(
    text: str = Form(...),
    language: str = Form(default="en")
):
    """
    Converts text → speech
    """

    try:
        audio_path = generate_speech(text, language)

        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()

        return {
            "success": True,
            "audio": audio_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
#  SPEECH TO TEXT ONLY
# ==========================================================

@router.post("/stt")
async def speech_to_text_api(
    audio: UploadFile = File(...),
    language: str = Form(default="en")
):
    """
    Converts speech → text only
    """

    temp_input_path = f"{TEMP_DIR}/audio_{int(time.time())}_{audio.filename}"

    try:
        with open(temp_input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        transcript = transcribe_audio(temp_input_path, language=language)

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        return {
            "success": True,
            "transcript": transcript
        }

    except Exception as e:

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

        raise HTTPException(status_code=500, detail=str(e))