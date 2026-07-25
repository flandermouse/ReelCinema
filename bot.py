import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from openai import AsyncOpenAI


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("BOT_TOKEN:", bool(BOT_TOKEN))
print("GROQ_API_KEY:", bool(GROQ_API_KEY))


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎬 Привет!\n\n"
        "Я ReelCinema AI.\n\n"
        "Напиши продукт или идею, "
        "и я придумаю рекламный ролик."
    )


@dp.message(F.text)
async def generate(message: Message):
    try:

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": """
Ты профессиональный режиссер рекламы,
креативный директор и сценарист.

Создавай идеи вирусных рекламных роликов
для TikTok, Reels и YouTube Shorts.

Думай как кинорежиссер:
- сильный хук в первые секунды
- эмоция
- визуальные детали
- камера
- свет
- монтаж
"""
                },

                {
                    "role": "user",
                    "content": f"""
Придумай рекламный ролик:

{message.text}

Структура ответа:

🔥 Хук (первые 3 секунды)

🎬 Сценарий

📷 План кадров
(ракурс, движение камеры, свет)

🎙 Озвучка

🎨 Визуальный стиль
"""
                }
            ]
        )


        answer = response.choices[0].message.content

        await message.answer(answer)


    except Exception as e:
        await message.answer(
            f"Ошибка генерации:\n{e}"
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())