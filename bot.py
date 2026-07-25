import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from google import genai


# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Проверка переменных (увидишь в Railway Logs)
print("BOT_TOKEN:", bool(BOT_TOKEN))
print("GEMINI_API_KEY:", bool(GEMINI_API_KEY))


if not BOT_TOKEN:
    raise ValueError("Нет BOT_TOKEN")

if not GEMINI_API_KEY:
    raise ValueError("Нет GEMINI_API_KEY")


# Telegram
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎬 Привет!\n\n"
        "Я ReelCinema AI.\n\n"
        "Напиши продукт или идею — я придумаю рекламный ролик."
    )


@dp.message(F.text)
async def generate(message: Message):
    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Ты профессиональный режиссер рекламы и сценарист.

Пользователь хочет рекламный ролик:

{message.text}

Создай идею в структуре:

🔥 Хук (первые 3 секунды)

🎬 Сценарий ролика

📷 План кадров по секундам

🎙 Текст диктора

🎨 Визуальный стиль и настроение

Ответь на русском языке.
"""
        )

        await message.answer(response.text)

    except Exception as e:
        print("GEMINI ERROR:", e)
        await message.answer(
            f"Ошибка генерации:\n{e}"
        )


async def main():

    print("🚀 ReelCinema AI запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())