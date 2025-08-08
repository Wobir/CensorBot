import yaml
import os

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

BOT_TOKEN = config["bot_token"]
TARGET_CHAT_ID = config["target_chat_id"]
LOG_LEVEL = config.get("log_level", "INFO")