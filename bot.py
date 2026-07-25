import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

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
# AI CLIENT
# =========================

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


# =========================
# TELEGRAM
# =========================

bot = Bot(BOT_TOKEN)

dp = Dispatcher(
    storage=MemoryStorage()
)


# =========================
# STATES
# =========================

class FilmCreation(StatesGroup):

    idea = State()
    genre = State()
    hero = State()
    format = State()
    camera = State()



# =========================
# DIRECTOR PROMPT
# =========================

SYSTEM_PROMPT = """

Ты — ReelCinema AI.

Ты профессиональный режиссер,
сценарист и оператор-постановщик.

Твоя задача:
помочь новичку снять настоящий фильм.


Главный принцип:

НЕ пиши как обычный AI.

Не давай общие советы.

Думай как режиссер перед съемкой.


Пользователь чаще всего снимает один.

Если камера iPhone:

используй только:

- iPhone 0.5x
- iPhone 1x
- iPhone 2x


Не используй:

- Sony
- Canon
- объективы
- профессиональную технику


Создай сначала весь фильм.


ФОРМАТ:


🎬 НАЗВАНИЕ


🎭 ЖАНР


❤️ ГЛАВНАЯ ЭМОЦИЯ


Что должен почувствовать зритель.


🎯 ТЕМА

О чем фильм на самом деле.


👤 ГЕРОЙ

Кто он.

Чего хочет.

Чего боится.

Что меняется внутри него.


====================


🎞 ПОЛНЫЙ ФИЛЬМ


АКТ 1

Сцена 1:
Название.
Что происходит.
Зачем нужна.


Сцена 2:


Сцена 3:



АКТ 2

Сцена 4:


Сцена 5:


Сцена 6:



АКТ 3

Сцена 7:


Финал:



====================


После полного фильма:


🎥 ПЕРВАЯ СЦЕНА ПОДРОБНО


Раскрой только первую сцену.


Минимум 8 кадров.


Каждый кадр:


КАДР №


Длительность:


Что видит зритель:


План:


Камера:


Где стоит телефон:


Движение:


Композиция:


Свет:


Звук:


Почему этот кадр работает:


====================


Запрещено писать:

"создать атмосферу"

"добавить драматизма"

"усилить напряжение"


Вместо этого:

показывай конкретное действие.


Пиши так, будто завтра съемочный день.
"""
# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await state.set_state(
        FilmCreation.idea
    )

    print(
        "START STATE:",
        await state.get_state()
    )


    await message.answer(
        "🎬 Добро пожаловать в ReelCinema.\n\n"
        "Я твой AI-режиссер.\n\n"
        "Ты даешь идею — я превращаю ее в фильм:\n\n"
        "🎭 история\n"
        "🎬 сцены\n"
        "📱 съемка на iPhone\n"
        "💡 свет\n"
        "🔊 звук\n"
        "✂️ монтаж\n\n"
        "Начнем.\n\n"
        "О чем будет твой фильм?"
    )



# =========================
# IDEA
# =========================

@dp.message(FilmCreation.idea)
async def get_idea(
    message: Message,
    state: FSMContext
):

    print(
        "IDEA RECEIVED:",
        message.text
    )


    await state.update_data(
        idea=message.text
    )


    await state.set_state(
        FilmCreation.genre
    )


    print(
        "NEXT STATE:",
        await state.get_state()
    )


    await message.answer(
        "Отлично.\n\n"
        "Какой жанр?\n\n"
        "Например:\n"
        "🎭 драма\n"
        "😱 хоррор\n"
        "🧠 триллер\n"
        "😂 комедия"
    )



# =========================
# GENRE
# =========================

@dp.message(FilmCreation.genre)
async def get_genre(
    message: Message,
    state: FSMContext
):

    print(
        "GENRE RECEIVED:",
        message.text
    )


    await state.update_data(
        genre=message.text
    )


    await state.set_state(
        FilmCreation.hero
    )


    print(
        "NEXT STATE:",
        await state.get_state()
    )


    await message.answer(
        "Кто главный герой?"
    )



# =========================
# HERO
# =========================

@dp.message(FilmCreation.hero)
async def get_hero(
    message: Message,
    state: FSMContext
):

    print(
        "HERO RECEIVED:",
        message.text
    )


    await state.update_data(
        hero=message.text
    )


    await state.set_state(
        FilmCreation.format
    )


    await message.answer(
        "Какой формат фильма?\n\n"
        "Например:\n"
        "короткометражка 5 минут\n"
        "Reels 60 секунд\n"
        "YouTube фильм"
    )



# =========================
# FORMAT
# =========================

@dp.message(FilmCreation.format)
async def get_format(
    message: Message,
    state: FSMContext
):

    print(
        "FORMAT RECEIVED:",
        message.text
    )


    await state.update_data(
        format=message.text
    )


    await state.set_state(
        FilmCreation.camera
    )


    await message.answer(
        "На что снимаем?\n\n"
        "Если ничего нет — напиши iPhone."
    )



# =========================
# CAMERA + GENERATION
# =========================

@dp.message(FilmCreation.camera)
async def generate(
    message: Message,
    state: FSMContext
):

    print(
        "CAMERA RECEIVED:",
        message.text
    )


    await state.update_data(
        camera=message.text
    )


    data = await state.get_data()


    await message.answer(
        "🎬 Создаю фильм...\n\n"
        "Строю историю и первую сцену."
    )


    prompt = f"""

Создай фильм.


Идея:

{data.get('idea')}


Жанр:

{data.get('genre')}


Герой:

{data.get('hero')}


Формат:

{data.get('format')}


Камера:

{data.get('camera') or 'iPhone'}

"""


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
                    "content": prompt
                }

            ],

            temperature=0.8,

            max_tokens=7000
        )


        answer = response.choices[0].message.content


        for i in range(
            0,
            len(answer),
            4000
        ):

            await message.answer(
                answer[i:i+4000]
            )


    except Exception as e:

        print(
            "AI ERROR:",
            e
        )

        await message.answer(
            f"Ошибка генерации:\n{e}"
        )


    await state.clear()



# =========================
# FALLBACK
# =========================

@dp.message()
async def fallback(
    message: Message,
    state: FSMContext
):

    current = await state.get_state()


    print(
        "FALLBACK:",
        message.text,
        "STATE:",
        current
    )


    await message.answer(
        "Я потерял текущий шаг.\n\n"
        "Нажми /start и начнем заново."
    )



# =========================
# RUN
# =========================

async def main():

    print(
        "ReelCinema AI запущен"
    )


    await dp.start_polling(bot)



if __name__ == "__main__":

    asyncio.run(main())