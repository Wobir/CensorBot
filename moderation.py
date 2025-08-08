import logging
from typing import Union, Dict, Any
import os

# Ленивая загрузка моделей для оптимизации памяти
_model_text = None
_model_audio = None

def _get_text_model():
    """Ленивая загрузка модели для текста."""
    global _model_text
    if _model_text is None:
        try:
            from detoxify import Detoxify
            _model_text = Detoxify('multilingual')
            logging.info("Модель Detoxify загружена успешно")
        except ImportError:
            logging.error("Библиотека detoxify не установлена")
            raise
        except Exception as e:
            logging.error(f"Ошибка загрузки модели Detoxify: {e}")
            raise
    return _model_text

def _get_audio_model():
    """Ленивая загрузка модели для аудио."""
    global _model_audio
    if _model_audio is None:
        try:
            import whisper
            _model_audio = whisper.load_model("base")
            logging.info("Модель Whisper загружена успешно")
        except ImportError:
            logging.error("Библиотека whisper не установлена")
            raise
        except Exception as e:
            logging.error(f"Ошибка загрузки модели Whisper: {e}")
            raise
    return _model_audio

def is_text_offensive(text: Union[str, None]) -> bool:
    """
    Проверяет текст на наличие оскорбительного контента.
    
    Args:
        text: Текст для проверки
        
    Returns:
        True если текст оскорбительный, иначе False
    """
    if not text or not isinstance(text, str) or not text.strip():
        return False
    
    try:
        model = _get_text_model()
        result: Dict[str, float] = model.predict(text)
        toxic_score: float = result.get("toxicity", 0.0)
        logging.debug(f"Оценка токсичности текста: {toxic_score}")
        return toxic_score > 0.7
    except Exception as e:
        logging.error(f"Ошибка при проверке текста на оскорбительность: {e}", exc_info=True)
        return False

def transcribe_audio(path: str) -> str:
    """
    Расшифровывает аудио файл в текст.
    
    Args:
        path: Путь к аудио файлу
        
    Returns:
        Расшифрованный текст
    """
    if not path or not os.path.exists(path):
        logging.warning(f"Аудио файл не найден: {path}")
        return ""
    
    try:
        model = _get_audio_model()
        logging.debug(f"Расшифровка аудио: {path}")
        result: Dict[str, Any] = model.transcribe(path)
        return result.get("text", "").strip()
    except Exception as e:
        logging.error(f"Ошибка при расшифровке аудио: {e}", exc_info=True)
        return ""

def is_audio_offensive(path: str) -> bool:
    """
    Проверяет аудио на наличие оскорбительного контента.
    
    Args:
        path: Путь к аудио файлу
        
    Returns:
        True если аудио содержит оскорбительный контент, иначе False
    """
    try:
        text = transcribe_audio(path)
        return is_text_offensive(text)
    except Exception as e:
        logging.error(f"Ошибка при проверке аудио на оскорбительность: {e}", exc_info=True)
        return False