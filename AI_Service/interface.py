from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

from src.stt.transcriber import transcribe_audio
from src.tts.generator import generate_audio_response
from src.engine.translator import translate_to_english, translate_to_user_language

app = FastAPI()

@app.post("/api/assess-voice")
async def process_voice_assessment(audio: UploadFile = File(...)):
    # Make sure the data folder exists to store temporary files
    os.makedirs("data", exist_ok=True)
    
    # 1. Save incoming audio temporarily
    temp_input_path = f"data/temp_{audio.filename}"
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        # 2. Ears (STT) - Get text and language
        original_text, user_lang = transcribe_audio(temp_input_path)
        print(f"User said ({user_lang}): {original_text}")
        
        # 3. Brain Prep (Translation to EN)
        english_text = translate_to_english(original_text, user_lang)
        print(f"Translated to English: {english_text}")
        
        # 4. RAG Pipeline (Your teammate will hook their Pinecone logic here)
        # english_feedback = src.rag.retriever.run_rag(english_text)
        
        # --- MOCK FEEDBACK FOR TESTING ---
        english_feedback = "Your explanation of the T-joint is good, but you forgot to mention measuring the wood with a try square first."
        print(f"AI Feedback: {english_feedback}")
        
        # 5. Brain Output (Translation back to User Lang)
        final_localized_text = translate_to_user_language(english_feedback, user_lang)
        print(f"Localized Feedback: {final_localized_text}")
        
        # 6. Mouth (TTS) - Generate spoken audio
        output_audio_path = f"data/response_{audio.filename}.mp3"
        generate_audio_response(final_localized_text, user_lang, output_filename=output_audio_path)
        
        # Return the audio file directly to the frontend
        return FileResponse(output_audio_path, media_type="audio/mpeg")
        
    finally:
        # Clean up the input file so your server doesn't run out of storage
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)