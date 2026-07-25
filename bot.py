import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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
# CLIENT
# =========================

bot = Bot(BOT_TOKEN)

dp = Dispatcher()

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


# =========================
# STATES
# =========================

class CinemaState(StatesGroup):
    mode = State()
    task = State()



# =========================
# MENUS
# =========================

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 Создать видео"),
            KeyboardButton(text="💡 Придумать идею")
        ],
        [
            KeyboardButton(text="📷 Помощь со съемкой"),
            KeyboardButton(text="🎙 Работа с текстом")
        ],
        [
            KeyboardButton(text="🛒 Реклама"),
            KeyboardButton(text="📚 Мои проекты")
        ]
    ],
    resize_keyboard=True
)


video_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎥 Фильм"),
            KeyboardButton(text="📱 Reels / Shorts")
        ],
        [
            KeyboardButton(text="📺 YouTube"),
            KeyboardButton(text="🎞 Сцена")
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ],
    resize_keyboard=True
)


shoot_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎥 Камера"),
            KeyboardButton(text="💡 Свет")
        ],
        [
            KeyboardButton(text="🎬 Композиция"),
            KeyboardButton(text="🎞 Движение камеры")
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ],
    resize_keyboard=True
)


# =========================
# PROMPTS
# =========================

base_prompt = """
Ты — ReelCinema AI.
Ты профессиональный режиссер, оператор и сценарист.

Отвечай как креативный директор кино.

Всегда учитывай:
- драматургию
- визуальный язык
- композицию
- движение камеры
- свет
- звук
- монтаж

Давай конкретные решения, а не общие советы.
"""


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "🎬 ReelCinema AI\n\n"
        "Твой виртуальный режиссер.\n\n"
        "Что будем делать?",
        reply_markup=main_menu
    )


# =========================
# MAIN MENU
# =========================

@dp.message(F.text=="🎬 Создать видео")
async def create_video(message: Message, state:FSMContext):

    await state.set_state(CinemaState.mode)

    await message.answer(
        "Что создаём?",
        reply_markup=video_menu
    )



@dp.message(F.text=="📷 Помощь со съемкой")
async def shooting(message: Message):

    await message.answer(
        "Что нужно разобрать?",
        reply_markup=shoot_menu
    )



@dp.message(F.text=="⬅️ Назад")
async def back(message: Message):

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu
    )



# =========================
# QUICK MODES
# =========================

@dp.message(
    F.text.in_([
        "💡 Придумать идею",
        "🎙 Работа с текстом",
        "🛒 Реклама",
        "📚 Мои проекты"
    ])
)
async def quick_mode(message: Message, state:FSMContext):

    await state.update_data(
        mode=message.text
    )

    await message.answer(
        f"{message.text}\n\n"
        "Расскажи задачу:"
    )



# =========================
# GENERATION
# =========================

@dp.message()
async def generate(message: Message, state:FSMContext):

    data = await state.get_data()

    mode = data.get(
        "mode",
        "Создание видео"
    )


    prompt = f"""
Режим:
{mode}

Запрос пользователя:
{message.text}


Создай результат в формате:

🔥 Главная идея

🎬 Сценарий

📷 Кадры

🎥 Камера

💡 Свет

🎙 Звук

🎞 Монтаж
"""


    try:

        await message.answer(
            "🎬 Думаю как режиссер..."
        )


        response = await client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role":"system",
                    "content":base_prompt
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.8,
            max_tokens=3000
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

    print("ReelCinema AI запущен")

    await dp.start_polling(bot)



if __name__ == "__main__":

    asyncio.run(main())