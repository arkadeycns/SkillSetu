from fastapi import APIRouter
from schemas.tts_schemas import TTSRequest
from AI_Service.src.tts.generator import generate_speech

router = APIRouter(prefix="/api/v1")

@router.post("/text-to-speech")
def text_to_speech(text: str, language: str = "en"):

    audio_file = generate_speech(text, language)

    return {
        "audio_file": audio_file
        }