# src/stt/transcriber.py
from groq import Groq
from src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def transcribe_audio(file_path):
    """Takes an audio file, returns text and detected language code."""
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json", 
        )
    return transcription.text, transcription.language