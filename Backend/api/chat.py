from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import time
import shutil
import base64

from AI_Service.src.stt.transcriber import transcribe_audio
from AI_Service.src.tts.generator import generate_speech
# Make sure this import matches where your helpers.py is located!
from AI_Service.src.rag.helpers import generate_greeting, generate_chat_response 

router = APIRouter(prefix="/api/chat", tags=["Guidance Chat"])

TEMP_DIR = "temp_data"
os.makedirs(TEMP_DIR, exist_ok=True)


session_histories = {}


@router.post("/start")
async def start_chat(
    session_id: str = Form(...),
    language: str = Form("en"),
    skill: str = Form(None)
):
    try:
        # Initialize empty history
        session_histories[session_id] = []
        
        user_data = {"role": skill} if skill else {}
        
        # Generate the greeting text
        greeting_text = generate_greeting(user_data=user_data, language=language)
        
        # Convert greeting to speech
        audio_base64 = None
        try:
            audio_path = generate_speech(greeting_text, language)
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            print("Chat Start TTS ERROR:", e)

        return JSONResponse({
            "greeting": greeting_text,
            "audio": audio_base64,
        })

    except Exception as e:
        print("CHAT START ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def process_chat(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    language: str = Form("en"),
    skill: str = Form(None)
):
    temp_input_path = f"{TEMP_DIR}/chat_in_{int(time.time())}_{audio.filename}"
    
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        # 1. Transcribe the user's voice
        user_message = transcribe_audio(temp_input_path, language="en")
        
        # Get history
        history = session_histories.get(session_id, [])
        user_data = {"role": skill} if skill else {}

        # 2. Get AI Response
        reply_text = generate_chat_response(
            message=user_message,
            user_data=user_data,
            history=history,
            language=language,
            selected_role=skill 
        )

        # 3. Save to history for the next turn
        history.append({"question": user_message, "answer_en": reply_text})
        session_histories[session_id] = history

        # 4. Convert response to speech
        audio_base64 = None
        try:
            audio_path = generate_speech(reply_text, language)
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            print("Chat TTS ERROR:", e)

        return JSONResponse({
            "reply": reply_text,
            "audio": audio_base64,
        })

    except Exception as e:
        print("CHAT PROCESS ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
