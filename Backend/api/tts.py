from fastapi import APIRouter
from schemas.tts_schemas import TTSRequest
from services.tts_service import generate_speech

router = APIRouter(prefix="/api/v1")

@router.post("/text-to-speech")
def text_to_speech(text: str):

    audio_file = generate_speech(text)

    return {
        "audio_file": audio_file
        }