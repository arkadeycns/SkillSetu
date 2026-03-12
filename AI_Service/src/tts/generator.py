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

def generate_audio_response(text, language_code, output_filename="data/response.mp3"):
    """Takes localized text and saves it as an MP3 file."""

    try:
        # Convert language name → ISO code
        lang = LANGUAGE_MAP.get(language_code, "en")

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_filename)

        return output_filename

    except Exception as e:
        print(f"TTS Error with language {language_code}: {e}")

        # fallback to English
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_filename)

        return output_filename