from AI_Service.src.stt.transcriber import transcribe_audio as stt_engine


def transcribe_audio(file):
    """
    Calls the STT engine from AI_Service.
    """
    transcript = stt_engine(file)
    return transcript
