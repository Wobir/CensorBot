import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ContentType

from config import BOT_TOKEN, TARGET_CHAT_ID, LOG_LEVEL
from moderation import is_text_offensive, is_image_offensive, is_audio_offensive
from utils import save_file, delete_file

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def moderate_and_replace(
    message: types.Message,
    check_func,
    warning_text: str,
    file_extractor=None  # функция: message -> путь или содержимое для проверки
):
    if message.chat.id != TARGET_CHAT_ID:
        return

    try:
        # Если есть функция извлечения файла — получаем путь или данные
        data = None
        if file_extractor:
            data = await file_extractor(message)
        else:
            data = message.text or ""

        # Проверяем на непристойность
        if await check_func(data) if asyncio.iscoroutinefunction(check_func) else check_func(data):
            await message.reply(warning_text)
            await message.delete()
            logger.info(f"Удалено сообщение пользователя {message.from_user.id} в чате {message.chat.id}")
        
        # Если был файл — удаляем временный файл
        if file_extractor and isinstance(data, str):
            delete_file(data)

    except Exception as e:
        logger.error(f"Ошибка при модерации сообщения: {e}")


async def extract_photo_path(message: types.Message) -> str:
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_data = await bot.download_file(file.file_path)
    path = save_file(file_data.read(), f"{photo.file_unique_id}.jpg")
    return path


async def extract_audio_path(message: types.Message) -> str:
    audio = message.voice or message.audio
    file = await bot.get_file(audio.file_id)
    file_data = await bot.download_file(file.file_path)
    path = save_file(file_data.read(), f"{audio.file_unique_id}.ogg")
    return path


@dp.message(F.content_type == ContentType.TEXT)
async def moderate_text(message: types.Message):
    await moderate_and_replace(
        message=message,
        check_func=is_text_offensive,
        warning_text="⚠️ Ваше сообщение было удалено, так как содержало неприемлемый контент."
    )


@dp.message(F.content_type == ContentType.PHOTO)
async def moderate_photo(message: types.Message):
    await moderate_and_replace(
        message=message,
        check_func=is_image_offensive,
        warning_text="⚠️ Ваше фото было удалено, так как содержало неприемлемый контент.",
        file_extractor=extract_photo_path
    )


@dp.message(F.content_type.in_([ContentType.AUDIO, ContentType.VOICE]))
async def moderate_audio(message: types.Message):
    await moderate_and_replace(
        message=message,
        check_func=is_audio_offensive,
        warning_text="⚠️ Ваше аудио было удалено, так как содержало неприемлемый контент.",
        file_extractor=extract_audio_path
    )


@dp.message(F.content_type == ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    try:
        await message.reply("Видео пока не анализируется.")
    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
