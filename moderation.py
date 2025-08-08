import logging
from detoxify import Detoxify
import whisper

model_text = Detoxify('multilingual')
model_audio = whisper.load_model("base")

def is_text_offensive(text: str) -> bool:
    if not text:
        return False
    result = model_text.predict(text)
    toxic_score = result.get("toxicity", 0)
    logging.debug(f"Оценка токсичности текста: {toxic_score}")
    return toxic_score > 0.7

def transcribe_audio(path: str) -> str:
    logging.debug(f"Расшифровка аудио: {path}")
    result = model_audio.transcribe(path)
    return result.get("text", "")

def is_audio_offensive(path: str) -> bool:
    text = transcribe_audio(path)
    return is_text_offensive(text)
