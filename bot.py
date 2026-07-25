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
# GROQ
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
# NEW DIRECTOR PROMPT
# =========================

SYSTEM_PROMPT = """

Ты — ReelCinema AI.

Ты не копирайтер.
Ты не пишешь общие советы.

Ты — режиссер, оператор-постановщик и монтажер,
который помогает новичку снять настоящий фильм.

Главная задача:
превратить идею человека в реальный съемочный план.

ВАЖНО:

Пользователь чаще всего снимает один.
По умолчанию камера — iPhone.

Каждый совет должен быть выполнимым.


Перед созданием фильма подумай:

1. Что зритель должен почувствовать?
2. Какой главный конфликт?
3. Какой вопрос заставит зрителя смотреть дальше?
4. Что мы показываем?
5. Что мы скрываем?


НЕ ИСПОЛЬЗУЙ фразы:

- "создать атмосферу"
- "усилить напряжение"
- "добавить драматизма"
- "использовать музыку для эмоций"

Вместо этого показывай конкретные действия.


ФОРМАТ:


🎬 НАЗВАНИЕ


🎭 ЖАНР


❤️ ЭМОЦИЯ ЗРИТЕЛЯ

Что зритель должен почувствовать.


❓ ГЛАВНЫЙ ВОПРОС

Почему человек продолжит смотреть?


👤 ГЕРОЙ

Кто он.

Чего хочет.

Чего боится.

Что изменится к концу фильма.


🎞 СТРУКТУРА


АКТ 1

Что происходит.


АКТ 2

Как растет конфликт.


АКТ 3

Какое изменение происходит.


====================

ДАЛЬШЕ ПО КАЖДОЙ СЦЕНЕ:


🎬 СЦЕНА №


Название:


Задача сцены:


Что должен почувствовать зритель:


Локация:


Время суток:


Действие:


====================

РАСКАДРОВКА


КАДР 1

Длительность:

План:
(общий / средний / крупный / макро)

Камера:
(iPhone 1x / 2x / 0.5)

Положение камеры:

Движение камеры:

Композиция:

Свет:

Звук:

Что чувствует зритель:

Почему этот кадр работает:


КАДР 2


КАДР 3


====================


🎥 ОПЕРАТОРСКИЕ ПРИЕМЫ

Объясни конкретно:

- где поставить камеру;
- когда приблизиться;
- когда оставить героя маленьким в кадре;
- где использовать тишину.


====================


✂️ МОНТАЖ


Укажи:

- длительность планов;
- где нужна пауза;
- где сменить темп;
- где скрыть информацию.


====================


🔊 ЗВУК


Опиши конкретно:

Например:

Не:
"тревожная музыка"

А:
"оставить только звук холодильника и дыхание героя первые 10 секунд"


====================


🎯 ФИНАЛЬНЫЙ РЕЖИССЕРСКИЙ СОВЕТ

Почему этот фильм может удержать зрителя.


Пиши как режиссер на съемочной площадке.

Не объясняй теорию кино.

Давай действия.
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
        "STATE:",
        await state.get_state()
    )


    await message.answer(
        "🎬 Добро пожаловать в ReelCinema.\n\n"
        "Я помогу тебе снять настоящий фильм.\n\n"
        "Не просто сценарий, а:\n"
        "🎭 историю\n"
        "🎬 сцены\n"
        "📱 кадры на iPhone\n"
        "💡 свет\n"
        "🔊 звук\n"
        "✂️ монтаж\n\n"
        "Я буду думать как режиссер.\n\n"
        "Первый вопрос:\n\n"
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
        "IDEA:",
        message.text
    )


    await state.update_data(
        idea=message.text
    )


    await state.set_state(
        FilmCreation.genre
    )


    await message.answer(
        "Отлично.\n\n"
        "Теперь выберем жанр.\n\n"
        "Например:\n"
        "😱 хоррор\n"
        "🎭 драма\n"
        "🧠 психологический триллер\n"
        "😂 комедия\n"
        "🚀 фантастика"
    )



# =========================
# GENRE
# =========================

@dp.message(FilmCreation.genre)
async def get_genre(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        genre=message.text
    )


    await state.set_state(
        FilmCreation.hero
    )


    await message.answer(
        "Кто главный герой?\n\n"
        "Опиши его.\n"
        "Например:\n"
        "Блогер, который устал притворяться успешным."
    )



# =========================
# HERO
# =========================

@dp.message(FilmCreation.hero)
async def get_hero(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        hero=message.text
    )


    await state.set_state(
        FilmCreation.format
    )


    await message.answer(
        "Какой формат фильма?\n\n"
        "Например:\n\n"
        "🎬 короткометражка 5 минут\n"
        "📱 серия Reels 60 секунд\n"
        "🎥 YouTube фильм"
    )



# =========================
# FORMAT
# =========================

@dp.message(FilmCreation.format)
async def get_format(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        format=message.text
    )


    await state.set_state(
        FilmCreation.camera
    )


    await message.answer(
        "На что снимаем?\n\n"
        "По умолчанию — iPhone.\n\n"
        "Напиши:\n"
        "iPhone\n"
        "или свою камеру."
    )



# =========================
# GENERATE
# =========================

@dp.message(FilmCreation.camera)
async def generate(
    message: Message,
    state: FSMContext
):


    await state.update_data(
        camera=message.text
    )


    data = await state.get_data()


    await message.answer(
        "🎬 Разрабатываю фильм...\n\n"
        "Анализирую конфликт, сцены и съемку."
    )


    prompt = f"""

Создай режиссерский план фильма.


Идея:

{data.get('idea')}


Жанр:

{data.get('genre')}


Главный герой:

{data.get('hero')}


Формат:

{data.get('format')}


Камера:

{data.get('camera') or 'iPhone'}


Создай подробный съемочный документ.
"""


    try:

        response = await client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role":"system",
                    "content":SYSTEM_PROMPT
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ],

            temperature=0.85,

            max_tokens=6000

        )


        answer = response.choices[0].message.content


        # Telegram максимум ~4000 символов

        for i in range(
            0,
            len(answer),
            4000
        ):

            await message.answer(
                answer[i:i+4000]
            )


    except Exception as e:

        await message.answer(
            f"Ошибка генерации:\n{e}"
        )


    await state.clear()



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