import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from google import genai

load_dotenv()
print("BOT_TOKEN:", bool(BOT_TOKEN))
print("GEMINI:", bool(GEMINI_API_KEY))

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

client = genai.Client(api_key=GEMINI_API_KEY)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎬 Привет!\n\n"
        "Я ReelCinema AI.\n\n"
        "Напиши, что хочешь рекламировать, и я придумаю идею ролика."
    )


@dp.message(F.text)
async def generate(message: Message):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Ты профессиональный режиссер рекламы.

Пользователь написал:

{message.text}

Ответь на русском языке.

Структура ответа:

🔥 Хук

🎬 Сценарий

📷 План кадров

🎙 Озвучка
"""
        )

        await message.answer(response.text)

    except Exception as e:
        await message.answer(f"Ошибка:\n{e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())