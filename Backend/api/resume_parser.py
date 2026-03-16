from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx
import os

router = APIRouter()

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001/api/resume/parse")

ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/api/v1/resume/parse")
async def parse_resume(resume: UploadFile = File(...)):

    if resume.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF, DOCX, TXT allowed."
        )

    file_bytes = await resume.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

    files = {
        "resume": (resume.filename, file_bytes, resume.content_type)
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(AI_SERVICE_URL, files=files)

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="AI resume parser service failed"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=500,
            detail="Unable to connect to AI resume parser service"
        )