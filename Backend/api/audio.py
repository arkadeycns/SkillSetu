from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

AUDIO_DIR = "audio"


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(file_path, media_type="audio/mpeg")