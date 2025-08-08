import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ContentType

from config import BOT_TOKEN, TARGET_CHAT_ID, LOG_LEVEL
from moderation import is_text_offensive, is_audio_offensive
from utils import save_file, delete_file

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def moderate_and_warn(
    message: types.Message,
    check_func,
    content_type_name: str,
    file_extractor=None
):
    if message.chat.id != TARGET_CHAT_ID:
        return

    try:
        data = await file_extractor(message) if file_extractor else (message.text or "")
        is_offensive = await check_func(data) if asyncio.iscoroutinefunction(check_func) else check_func(data)

        if is_offensive:
            warning = f"⚠️ Ваше {content_type_name} было удалено, так как содержало неприемлемый контент."
            await message.reply(warning)
            await message.delete()
            logger.info(f"Удалено сообщение пользователя {message.from_user.id} в чате {message.chat.id}")

        if file_extractor and isinstance(data, str):
            delete_file(data)

    except Exception as e:
        logger.error(f"Ошибка при модерации ({content_type_name}): {e}")


async def extract_audio_path(message: types.Message) -> str:
    audio = message.voice or message.audio
    file = await bot.get_file(audio.file_id)
    file_data = await bot.download_file(file.file_path)
    return save_file(file_data.read(), f"{audio.file_unique_id}.ogg")


@dp.message(F.content_type == ContentType.TEXT)
async def handle_text(message: types.Message):
    await moderate_and_warn(
        message,
        is_text_offensive,
        "сообщение"
    )


@dp.message(F.content_type.in_([ContentType.AUDIO, ContentType.VOICE]))
async def handle_audio(message: types.Message):
    await moderate_and_warn(
        message,
        is_audio_offensive,
        "аудио",
        extract_audio_path
    )


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
