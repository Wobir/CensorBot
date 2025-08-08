import os
import tempfile
from typing import Union

# Константы
SAVE_DIR = os.getenv("TEMP_FILES_DIR", "temp_files")
DEFAULT_PERMISSIONS = 0o600  # Только владелец может читать/писать

def setup_temp_directory() -> str:
    """
    Создает и настраивает директорию для временных файлов.
    
    Returns:
        Путь к директории временных файлов
    """
    try:
        # Создание директории с безопасными правами доступа
        os.makedirs(SAVE_DIR, mode=0o700, exist_ok=True)
        return SAVE_DIR
    except PermissionError:
        # Если нет прав на создание в указанной директории, используем системную temp
        system_temp = tempfile.gettempdir()
        temp_save_dir = os.path.join(system_temp, "bot_temp_files")
        os.makedirs(temp_save_dir, mode=0o700, exist_ok=True)
        return temp_save_dir
    except Exception as e:
        raise RuntimeError(f"Ошибка создания директории для временных файлов: {e}")

# Инициализация директории при импорте
SAVE_DIR = setup_temp_directory()

def save_file(data: Union[bytes, bytearray], filename: str) -> str:
    """
    Сохраняет данные в файл с безопасными правами доступа.
    
    Args:
        data: Данные для сохранения
        filename: Имя файла
        
    Returns:
        Путь к сохраненному файлу
        
    Raises:
        ValueError: Если данные пусты или имя файла некорректно
        IOError: Если не удалось сохранить файл
    """
    if not data:
        raise ValueError("Данные для сохранения не могут быть пустыми")
    
    if not filename or not isinstance(filename, str):
        raise ValueError("Имя файла должно быть непустой строкой")
    
    # Санитизация имени файла
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    if not safe_filename:
        safe_filename = "temp_file"
    
    path = os.path.join(SAVE_DIR, safe_filename)
    
    try:
        with open(path, "wb") as f:
            os.chmod(path, DEFAULT_PERMISSIONS)  # Установка безопасных прав доступа
            f.write(data)
        return path
    except Exception as e:
        raise IOError(f"Ошибка сохранения файла {path}: {e}")

def delete_file(path: str) -> bool:
    """
    Удаляет файл безопасно.
    
    Args:
        path: Путь к файлу для удаления
        
    Returns:
        True если файл успешно удален, иначе False
    """
    if not path or not isinstance(path, str):
        return False
    
    try:
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
            return True
        return False
    except Exception as e:
        print(f"Ошибка при удалении файла {path}: {e}")
        return False