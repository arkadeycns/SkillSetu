from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import time
from services.stt_service import transcribe_audio

router = APIRouter(prefix="/api/v1")

@router.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):

    os.makedirs("temp_data", exist_ok=True)
    temp_input_path = f"temp_data/stt_{int(time.time())}_{audio.filename}"

    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        result = transcribe_audio(temp_input_path)
        text = result[0] if isinstance(result, tuple) else result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

    return {
        "transcription": text
    }