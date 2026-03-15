from gtts import gTTS
import uuid
import os

LANGUAGE_MAP = {
    "hindi": "hi",
    "english": "en",
    "tamil": "ta",
    "telugu": "te",
    "bengali": "bn",
    "marathi": "mr",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
}


def _normalize_language(language_code: str | None) -> str:
    normalized = (language_code or "").strip().lower()
    if not normalized:
        return "en"

    if normalized in LANGUAGE_MAP:
        return LANGUAGE_MAP[normalized]

    # Accept ISO-639-1 or regional values like hi-IN.
    if "-" in normalized:
        normalized = normalized.split("-", 1)[0]

    if len(normalized) == 2 and normalized.isalpha():
        return normalized

    return "en"


def generate_speech(text: str, language_code: str = "en"):
    
    # create unique filename
    filename = f"audio/audio_{uuid.uuid4()}.mp3"

    # create audio
    tts = gTTS(text=text, lang=_normalize_language(language_code))

    # save file
    tts.save(filename)

    return filename