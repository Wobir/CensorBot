from detoxify import Detoxify
import whisper
import logging

model_text = Detoxify('original')
model_audio = whisper.load_model("base")

def is_text_offensive(text: str) -> bool:
    result = model_text.predict(text)
    toxic_score = result["toxicity"]
    logging.debug(f"Оценка токсичности текста: {toxic_score}")
    return toxic_score > 0.7

def is_image_offensive(path: str) -> bool:
    # Пока что всегда безопасно
    logging.debug(f"Анализ изображения {path} (заглушка)")
    return False

def transcribe_audio(path: str) -> str:
    logging.debug(f"Расшифровка аудио: {path}")
    result = model_audio.transcribe(path)
    return result["text"]

def is_audio_offensive(path: str) -> bool:
    text = transcribe_audio(path)
    return is_text_offensive(text)
