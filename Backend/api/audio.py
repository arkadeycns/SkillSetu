from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

AUDIO_DIR = "generated_audio"


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "Audio file not found"}

    return FileResponse(file_path, media_type="audio/mpeg")