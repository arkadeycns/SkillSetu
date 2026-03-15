from stt.transcriber import transcribe_audio as stt_engine


def transcribe_audio(file):
    return stt_engine(file)
