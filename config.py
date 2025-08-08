import yaml
import os
from typing import Any, Dict

# Константы
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")
DEFAULT_LOG_LEVEL = "INFO"

# Валидация существования файла конфигурации
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Файл конфигурации не найден: {CONFIG_PATH}")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f)
except yaml.YAMLError as e:
    raise ValueError(f"Ошибка парсинга YAML файла конфигурации: {e}")
except Exception as e:
    raise RuntimeError(f"Ошибка чтения файла конфигурации: {e}")

# Валидация обязательных параметров
required_fields = ["bot_token", "target_chat_id"]
for field in required_fields:
    if field not in config:
        raise ValueError(f"Обязательное поле '{field}' отсутствует в конфигурации")

# Извлечение параметров с валидацией
BOT_TOKEN = str(config["bot_token"]).strip()
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не может быть пустым")

try:
    TARGET_CHAT_ID = int(config["target_chat_id"])
except (ValueError, TypeError) as e:
    raise ValueError(f"Некорректный формат TARGET_CHAT_ID: {e}")

LOG_LEVEL = str(config.get("log_level", DEFAULT_LOG_LEVEL)).upper()
ALLOWED_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if LOG_LEVEL not in ALLOWED_LOG_LEVELS:
    LOG_LEVEL = DEFAULT_LOG_LEVEL