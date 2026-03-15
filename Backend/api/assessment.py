from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse
import shutil
import os
import time

from services.stt_service import transcribe_audio
from services.rag_service import rag_query
from services.tts_service import generate_speech

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

def remove_temp_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            print(f"Cleanup error: {e}")

@router.post("/assess-voice")
async def process_voice_assessment(
    audio: UploadFile = File(...),
    question: str = Form("Explain the process of making a T-Joint."),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    os.makedirs("temp_data", exist_ok=True)
    os.makedirs("audio", exist_ok=True) 
    
    temp_input_path = f"temp_data/incoming_{int(time.time())}_{audio.filename}"
    
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        stt_result = transcribe_audio(temp_input_path)
        user_text = stt_result[0] if isinstance(stt_result, tuple) else stt_result
        print(f"STT Output: {user_text}")
        
        ai_feedback = rag_query(question, user_text)
        print(f"RAG Output: {ai_feedback}")
        
        output_audio_path = generate_speech(ai_feedback)

        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
            
        background_tasks.add_task(remove_temp_file, output_audio_path)
        return FileResponse(output_audio_path, media_type="audio/mpeg")
        
    except Exception as e:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        print(f"CRITICAL ERROR: {str(e)}")
        return {"error": str(e)}