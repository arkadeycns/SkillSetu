# src/tts/generator.py
from gtts import gTTS

LANGUAGE_MAP = {
    "Hindi": "hi",
    "English": "en",
    "Tamil": "ta",
    "Telugu": "te",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa"
}

ISO_LANG_WHITELIST = {
    "en",
    "hi",
    "ta",
    "te",
    "bn",
    "mr",
    "gu",
    "kn",
    "ml",
    "pa",
}

def generate_audio_response(text, language_code, output_filename="data/response.mp3"):
    """Takes localized text and saves it as an MP3 file."""

    try:
        normalized = (language_code or "").strip()
        # Accept either full language name or already-detected ISO code.
        if normalized in ISO_LANG_WHITELIST:
            lang = normalized
        else:
            lang = LANGUAGE_MAP.get(normalized, "en")

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_filename)

        return output_filename

    except Exception as e:
        print(f"TTS Error with language {language_code}: {e}")

        # fallback to English
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_filename)

        return output_filename


def generate_speech(text: str, language_code: str = "en", output_filename: str = "data/response.mp3") -> str:
    """Compatibility wrapper for callers expecting generate_speech."""
    return generate_audio_response(text=text, language_code=language_code, output_filename=output_filename)