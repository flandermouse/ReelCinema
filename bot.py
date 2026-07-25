import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

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


# =========================
# СОСТОЯНИЕ РЕЖИМА
# =========================

user_modes = {}


# =========================
# КНОПКИ
# =========================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 Реклама"),
            KeyboardButton(text="💡 Идея ролика")
        ],
        [
            KeyboardButton(text="📷 Раскадровка"),
            KeyboardButton(text="🎙 Озвучка")
        ]
    ],
    resize_keyboard=True
)


# =========================
# ПРОМПТЫ
# =========================

prompts = {

"🎬 Реклама": """
Ты креативный директор рекламных роликов.

Создай продающий рекламный ролик.

Структура:
🔥 Хук первые 3 секунды
🎬 Сценарий
📷 Кадры
🎥 Камера и движение
💡 Свет
🎙 Озвучка
🎨 Визуальный стиль

Думай как режиссер рекламы.
""",


"💡 Идея ролика": """
Ты генератор вирусных идей для Reels и TikTok.

Придумай 5 сильных идей.

Для каждой:
- хук
- конфликт
- эмоция
- финальный твист
""",


"📷 Раскадровка": """
Ты профессиональный оператор-постановщик.

Сделай раскадровку.

Для каждого кадра укажи:
- план
- объектив
- движение камеры
- композицию
- свет
- звук
""",


"🎙 Озвучка": """
Ты сценарист рекламной озвучки.

Создай:
- текст диктора
- интонацию
- паузы
- эмоциональную подачу
"""
}


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "🎬 ReelCinema AI\n\n"
        "Выбери режим создания:",
        reply_markup=menu
    )


# =========================
# ВЫБОР РЕЖИМА
# =========================

@dp.message(F.text.in_(prompts.keys()))
async def choose_mode(message: Message):

    user_modes[message.from_user.id] = message.text

    await message.answer(
        f"Выбран режим: {message.text}\n\n"
        "Теперь напиши продукт или идею."
    )


# =========================
# ГЕНЕРАЦИЯ
# =========================

@dp.message(F.text)
async def generate(message: Message):

    mode = user_modes.get(
        message.from_user.id,
        "🎬 Реклама"
    )


    try:

        response = await client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": prompts[mode]
                },

                {
                    "role": "user",
                    "content": message.text
                }

            ],

            temperature=0.8,
            max_tokens=2500
        )


        await message.answer(
            response.choices[0].message.content
        )


    except Exception as e:

        await message.answer(
            f"Ошибка:\n{e}"
        )


# =========================
# RUN
# =========================

async def main():

    print("ReelCinema запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())