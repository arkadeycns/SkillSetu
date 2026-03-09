from gtts import gTTS
import uuid
import os

def generate_speech(text: str):
    
    # create unique filename
    filename = f"audio/audio_{uuid.uuid4()}.mp3"

    # create audio
    tts = gTTS(text=text, lang="en")

    # save file
    tts.save(filename)

    return filename