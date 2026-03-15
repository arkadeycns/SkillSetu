# backend/api/assessment.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
import os
import time

# --- IMPORT AI SERVICES HERE ---
# Tell your friends to uncomment and fix these import paths to match their actual functions
from services.stt_service import transcribe_audio
# from services.rag_service import run_rag_pipeline 
# from services.tts_service import generate_tts_audio

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

def remove_temp_file(path: str):
    """Deletes files in the background after sending the response to keep the server clean."""
    if os.path.exists(path):
        os.remove(path)

@router.post("/assess-voice")
async def process_voice_assessment(
    audio: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # 1. Setup temporary storage
    os.makedirs("temp_data", exist_ok=True)
    
    # Save incoming webm file from React
    temp_input_path = f"temp_data/incoming_{int(time.time())}_{audio.filename}"
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        # 2. EARS: Run Speech-to-Text
        user_text = transcribe_audio(temp_input_path)
        print(f"STT Output: {user_text}")
        
        # 3. BRAIN: Run RAG (Pinecone / Llama)
        # --- UNCOMMENT WHEN RAG IS READY ---
        # ai_feedback = run_rag_pipeline(user_text)
        
        # --- MOCK RAG (Delete this when RAG is plugged in) ---
        ai_feedback = "Your answer was good, but you forgot to mention wearing safety goggles."
        print(f"RAG Output: {ai_feedback}")
        
        # 4. MOUTH: Run Text-to-Speech
        output_audio_path = f"temp_data/outgoing_{int(time.time())}.mp3"
        
        # --- UNCOMMENT WHEN TTS IS READY ---
        # generate_tts_audio(ai_feedback, output_audio_path)
        
        # --- MOCK TTS (Delete this when your TTS service is ready) ---
        from gtts import gTTS
        tts = gTTS(text=ai_feedback, lang='en', slow=False)
        tts.save(output_audio_path)
        # ------------------------------------------------------------

        # 5. Clean up the incoming webm file immediately
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
            
        # 6. Send MP3 to React, then delete it in the background
        background_tasks.add_task(remove_temp_file, output_audio_path)
        
        return FileResponse(output_audio_path, media_type="audio/mpeg")
        
    except Exception as e:
        # If anything crashes, delete the incoming file so the server doesn't clog up
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        return {"error": str(e)}