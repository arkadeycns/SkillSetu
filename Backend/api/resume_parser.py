from io import BytesIO

from fastapi import APIRouter, UploadFile, File, HTTPException

from AI_Service.src.parser.resume_parser import parse_resume as parse_resume_text
from AI_Service.src.parser.text_extractor import extract_text_from_pdf, extract_text_from_docx

router = APIRouter()

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

    try:
        if resume.content_type == "application/pdf":
            text = extract_text_from_pdf(BytesIO(file_bytes))
        elif resume.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(BytesIO(file_bytes))
        else:
            text = file_bytes.decode("utf-8", errors="ignore")

        text = (text or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from uploaded resume")

        return parse_resume_text(text)

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {exc}") from exc