from fastapi import APIRouter
from services.stt_service import transcribe_audio

router = APIRouter(prefix="/api/v1")

@router.post("/speech-to-text")
def speech_to_text():

    text = transcribe_audio(None)

    return {
        "transcription": text
    }