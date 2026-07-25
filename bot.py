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


# =====================
# СОСТОЯНИЯ
# =====================

class ReelForm(StatesGroup):

    mode = State()
    camera = State()
    device = State()
    product = State()
    style = State()
    platform = State()



# =====================
# КЛАВИАТУРЫ
# =====================


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 Создать ролик")
        ]
    ],
    resize_keyboard=True
)


camera_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📱 Телефон"),
            KeyboardButton(text="📷 Камера")
        ]
    ],
    resize_keyboard=True
)


style_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="😱 Хоррор"),
            KeyboardButton(text="🎬 Кино")
        ],
        [
            KeyboardButton(text="✨ Премиум"),
            KeyboardButton(text="😂 Комедия")
        ]
    ],
    resize_keyboard=True
)


platform_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="TikTok"),
            KeyboardButton(text="Reels")
        ],
        [
            KeyboardButton(text="YouTube Shorts")
        ]
    ],
    resize_keyboard=True
)



# =====================
# START
# =====================


@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "🎬 ReelCinema AI\n\n"
        "Я помогу создать рекламный ролик.\n\n"
        "Начинаем?",
        reply_markup=start_keyboard
    )



# =====================
# НАЧАЛО
# =====================


@dp.message(F.text=="🎬 Создать ролик")
async def create(message: Message, state:FSMContext):

    await state.set_state(ReelForm.camera)

    await message.answer(
        "На что снимаем?",
        reply_markup=camera_keyboard
    )



# =====================
# КАМЕРА
# =====================


@dp.message(ReelForm.camera)
async def camera(message:Message, state:FSMContext):

    await state.update_data(
        camera_type=message.text
    )


    await state.set_state(ReelForm.device)


    await message.answer(
        "Напиши модель камеры или телефона.\n\n"
        "Например:\n"
        "Sony ZV-E10 + Viltrox 35mm"
    )



# =====================
# МОДЕЛЬ
# =====================


@dp.message(ReelForm.device)
async def device(message:Message,state:FSMContext):

    await state.update_data(
        device=message.text
    )


    await state.set_state(ReelForm.product)


    await message.answer(
        "Что рекламируем?"
    )



# =====================
# ПРОДУКТ
# =====================


@dp.message(ReelForm.product)
async def product(message:Message,state:FSMContext):

    await state.update_data(
        product=message.text
    )

    await state.set_state(ReelForm.style)


    await message.answer(
        "Выбери стиль:",
        reply_markup=style_keyboard
    )



# =====================
# СТИЛЬ
# =====================


@dp.message(ReelForm.style)
async def style(message:Message,state:FSMContext):

    await state.update_data(
        style=message.text
    )

    await state.set_state(ReelForm.platform)


    await message.answer(
        "Где будет ролик?",
        reply_markup=platform_keyboard
    )



# =====================
# ФИНАЛ
# =====================


@dp.message(ReelForm.platform)
async def platform(message:Message,state:FSMContext):

    await state.update_data(
        platform=message.text
    )


    data = await state.get_data()


    prompt=f"""
Ты профессиональный режиссер рекламы.

Создай рекламный ролик.

Данные:

Камера:
{data['device']}

Тип съемки:
{data['camera_type']}

Продукт:
{data['product']}

Стиль:
{data['style']}

Платформа:
{data['platform']}


Ответ:

🔥 Хук первые 3 секунды

🎬 Сценарий

📷 Раскадровка:
- план
- объектив
- движение камеры
- свет

🎙 Озвучка

🎨 Цвет и стиль

🎞 Монтаж
"""


    await message.answer(
        "🎬 Создаю режиссерский план..."
    )


    response = await client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role":"system",
                "content":
                "Ты лучший режиссер рекламных роликов."
            },
            {
                "role":"user",
                "content":prompt
            }
        ],

        max_tokens=3000
    )


    await message.answer(
        response.choices[0].message.content
    )


    await state.clear()



# =====================


async def main():

    print("ReelCinema AI запущен")

    await dp.start_polling(bot)



if __name__=="__main__":

    asyncio.run(main())