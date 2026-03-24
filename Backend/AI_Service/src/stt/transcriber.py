# src/stt/transcriber.py

from groq import Groq
from AI_Service.src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def transcribe_audio(file_path, language="en"):
    """
    Transcribes speech using Groq Whisper.
    Language is provided by the session to avoid auto-detection.
    """

    with open(file_path, "rb") as file:

        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            language=language
        )

    return transcription.text