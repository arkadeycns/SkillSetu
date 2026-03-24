from gtts import gTTS
import uuid
import os

# Ensure audio folder exists
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Language mapping
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


# ==========================================================
# Normalize language input
# ==========================================================
def _normalize_language(language_code: str | None) -> str:
    if not language_code:
        return "en"

    lang = language_code.strip().lower()

    # 🔥 FIX: Handle Hinglish
    if lang == "hinglish":
        return "hi"

    # Map known languages
    if lang in LANGUAGE_MAP:
        return LANGUAGE_MAP[lang]

    # Handle formats like "en-IN", "hi-IN"
    if "-" in lang:
        lang = lang.split("-")[0]

    # Accept valid 2-letter codes
    if len(lang) == 2 and lang.isalpha():
        return lang

    return "en"


# ==========================================================
# OPTIONAL: Improve Hinglish pronunciation
# ==========================================================
def _preprocess_text(text: str, lang: str) -> str:
    if lang == "hi":
        # Very basic replacements (safe)
        text = text.replace("hai", "है")
        text = text.replace("nahi", "नहीं")
        text = text.replace("kaam", "काम")
    return text


# ==========================================================
# TEXT → SPEECH
# ==========================================================
def generate_speech(text: str, language_code: str = "en") -> str:
    """
    Converts text → speech and returns file path
    """

    try:
        if not text or not text.strip():
            raise ValueError("Empty text for TTS")

        lang = _normalize_language(language_code)

        # 🔥 Improve pronunciation
        processed_text = _preprocess_text(text, lang)

        # Unique filename
        filename = f"{AUDIO_DIR}/audio_{uuid.uuid4()}.mp3"

        # Generate speech
        tts = gTTS(text=processed_text, lang=lang)
        tts.save(filename)

        return filename

    except Exception as e:
        print("TTS ERROR:", e)
        raise e


# ==========================================================
# CLEANUP
# ==========================================================
def cleanup_audio_files(max_files: int = 50):
    try:
        files = [
            os.path.join(AUDIO_DIR, f)
            for f in os.listdir(AUDIO_DIR)
            if f.endswith(".mp3")
        ]

        files.sort(key=os.path.getctime)

        if len(files) > max_files:
            for f in files[:-max_files]:
                os.remove(f)

    except Exception as e:
        print("Cleanup failed:", e)
