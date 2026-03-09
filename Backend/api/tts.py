from fastapi import APIRouter
from services.tts_service import generate_speech

router = APIRouter()

@router.post("/tts")
def text_to_speech(text: str):

    audio_file = generate_speech(text)

    return {
        "message": "Speech generated successfully",
        "file": audio_file
    }