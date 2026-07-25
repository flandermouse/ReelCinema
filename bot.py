import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from openai import AsyncOpenAI


# =========================
# ENV
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("BOT_TOKEN:", bool(BOT_TOKEN))
print("GROQ_API_KEY:", bool(GROQ_API_KEY))


# =========================
# GROQ CLIENT
# =========================

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


# =========================
# TELEGRAM
# =========================

bot = Bot(BOT_TOKEN)

dp = Dispatcher()


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
Ты — профессиональный режиссер рекламы, сценарист и оператор-постановщик.

Твоя специализация:
- вирусные ролики TikTok / Reels / Shorts
- рекламные видео с киношной атмосферой
- хоррор, триллер, эмоциональные хуки
- постановка сцен

Отвечай как креативный директор.

Когда пользователь дает идею:
1. Усиливай хук первых 3 секунд.
2. Предлагай конкретные кадры.
3. Указывай:
   - план камеры
   - движение камеры
   - объектив
   - свет
   - композицию
   - звук
   - монтаж
4. Думай как режиссер, а не как копирайтер.

Не пиши банальные советы.
Давай конкретные съемочные решения.
"""


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎬 Я твой AI-режиссер.\n\n"
        "Напиши идею ролика — помогу сделать сценарий, кадры и постановку."
    )


# =========================
# CHAT
# =========================

@dp.message(F.text)
async def chat(message: Message):

    user_text = message.text

    try:

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],

            temperature=0.8,
            max_tokens=2500
        )


        answer = response.choices[0].message.content


        await message.answer(answer)


    except Exception as e:

        await message.answer(
            f"Ошибка генерации:\n{e}"
        )


# =========================
# RUN
# =========================

async def main():

    print("Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())