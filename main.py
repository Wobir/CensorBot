import asyncio
import logging
import os
from typing import Optional, Callable, Awaitable, Union

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, TARGET_CHAT_ID, LOG_LEVEL
from moderation import is_text_offensive, is_audio_offensive
from utils import save_file, delete_file

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


async def moderate_and_warn(
    message: types.Message,
    check_func: Callable[[Union[str, bytes]], Union[bool, Awaitable[bool]]],
    content_type_name: str,
    file_extractor: Optional[Callable[[types.Message], Awaitable[str]]] = None
) -> None:
    """
    Модерирует сообщение и предупреждает пользователя при необходимости.
    
    Args:
        message: Сообщение для модерации
        check_func: Функция проверки контента
        content_type_name: Название типа контента для логов
        file_extractor: Функция извлечения файла (если требуется)
    """
    if not message.chat or message.chat.id != TARGET_CHAT_ID:
        return

    try:
        # Извлечение данных для проверки
        data: Union[str, bytes] = ""
        file_path: Optional[str] = None
        
        if file_extractor:
            file_path = await file_extractor(message)
            data = file_path
        else:
            data = message.text or message.caption or ""
        
        # Проверка контента
        is_offensive = (
            await check_func(data) 
            if asyncio.iscoroutinefunction(check_func) 
            else check_func(data)
        )

        if is_offensive:
            warning = f"⚠️ Ваше <b>{content_type_name}</b> было удалено, так как содержало неприемлемый контент."
            try:
                await message.reply(warning)
                await message.delete()
                logger.info(
                    f"Удалено сообщение пользователя {message.from_user.id if message.from_user else 'unknown'} "
                    f"в чате {message.chat.id}"
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить предупреждение или удалить сообщение: {e}")

        # Очистка временных файлов
        if file_path and isinstance(file_path, str):
            delete_file(file_path)

    except Exception as e:
        logger.error(f"Ошибка при модерации ({content_type_name}): {e}", exc_info=True)


async def extract_audio_path(message: types.Message) -> str:
    """
    Извлекает аудио из сообщения и сохраняет его временно.
    
    Args:
        message: Сообщение с аудио
        
    Returns:
        Путь к сохраненному файлу
        
    Raises:
        ValueError: Если в сообщении нет аудио
    """
    audio = message.voice or message.audio
    if not audio:
        raise ValueError("Сообщение не содержит аудио")
    
    try:
        file = await bot.get_file(audio.file_id)
        file_data = await bot.download_file(file.file_path)
        file_content = await file_data.read()
        return save_file(file_content, f"{audio.file_unique_id}.ogg")
    except Exception as e:
        logger.error(f"Ошибка при загрузке аудио файла: {e}")
        raise


@dp.message(lambda message: message.content_type == ContentType.TEXT)
async def handle_text(message: types.Message) -> None:
    """Обработчик текстовых сообщений."""
    await moderate_and_warn(
        message,
        is_text_offensive,
        "сообщение"
    )


@dp.message(lambda message: message.content_type in [ContentType.AUDIO, ContentType.VOICE])
async def handle_audio(message: types.Message) -> None:
    """Обработчик аудио сообщений."""
    await moderate_and_warn(
        message,
        is_audio_offensive,
        "аудио",
        extract_audio_path
    )


@dp.errors()
async def error_handler(update: types.Update, exception: Exception) -> bool:
    """Глобальный обработчик ошибок."""
    logger.error(f"Ошибка при обработке обновления: {exception}", exc_info=True)
    return True


async def main() -> None:
    """Основная функция запуска бота."""
    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
        raise
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения работы")
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)