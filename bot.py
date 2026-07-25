import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

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

dp = Dispatcher()


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
# MEMORY START
# =========================

users_started = set()



# =========================
# PROMPT
# =========================

SYSTEM_PROMPT = """

Ты — ReelCinema AI.
Ты профессиональный режиссер, сценарист и оператор-постановщик.

Твоя задача — помочь человеку снять настоящий фильм,
даже если у него только телефон и нет команды.

По умолчанию съемка идет на iPhone,
если пользователь не указал другую камеру.


После получения идеи создай полноценный режиссерский пакет.


Структура ответа:


🎬 НАЗВАНИЕ ФИЛЬМА


🎭 ЖАНР


📝 ЛОГЛАЙН
О чем фильм в одном предложении.


👤 ГЛАВНЫЙ ГЕРОЙ
Кто он.
Чего хочет.
Чего боится.


🎞 СТРУКТУРА ИСТОРИИ

Акт 1:
Завязка.

Акт 2:
Конфликт.

Акт 3:
Развязка.


🎬 СЦЕНЫ


Для каждой сцены:

Название сцены:

Задача сцены:

Локация:

Эмоция:


КАДРЫ:

Кадр 1:
- план
- фокусное расстояние
- движение камеры
- композиция
- свет
- звук


Кадр 2:
...


🎥 ОПЕРАТОРСКОЕ РЕШЕНИЕ

Объясни:
- почему камера стоит именно так
- как создать эмоцию
- как удерживать внимание


✂️ МОНТАЖ

Укажи:
- темп
- паузы
- переходы
- моменты усиления напряжения


🔊 ЗВУК

Укажи:
- музыку
- атмосферу
- шумы


🎯 ПРИЕМЫ УДЕРЖАНИЯ ЗРИТЕЛЯ

Объясни:
- где создать вопрос
- где дать ответ
- где сделать поворот


Пиши как настоящий режиссер.
Не давай общие советы.
Давай конкретный съемочный план.
"""



# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    user_id = message.from_user.id


    if user_id not in users_started:

        users_started.add(user_id)


        await message.answer(
            "🎬 Добро пожаловать в ReelCinema.\n\n"
            "Я помогу превратить твою идею в настоящий фильм.\n\n"
            "Мы создадим:\n"
            "🎭 историю\n"
            "🎬 сцены\n"
            "📷 кадры\n"
            "💡 свет\n"
            "🔊 звук\n"
            "✂️ монтаж\n\n"
            "Начнем.\n\n"
            "О чем будет твой фильм?"
        )

        await FilmCreation.idea.set()

    else:

        await message.answer(
            "🎬 Продолжаем создавать фильм.\n\n"
            "О чем новая идея?"
        )

        await FilmCreation.idea.set()



# =========================
# IDEA
# =========================

@dp.message(FilmCreation.idea)
async def get_idea(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        idea=message.text
    )

    await state.set_state(
        FilmCreation.genre
    )


    await message.answer(
        "Отлично.\n\n"
        "Какой жанр?\n\n"
        "Например:\n"
        "драма, хоррор, триллер, комедия, фантастика"
    )



# =========================
# GENRE
# =========================

@dp.message(FilmCreation.genre)
async def get_genre(
    message: Message,
    state:FSMContext
):

    await state.update_data(
        genre=message.text
    )


    await state.set_state(
        FilmCreation.hero
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
    state:FSMContext
):

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
        "серия 1 минута\n"
        "YouTube фильм"
    )



# =========================
# FORMAT
# =========================

@dp.message(FilmCreation.format)
async def get_format(
    message: Message,
    state:FSMContext
):

    await state.update_data(
        format=message.text
    )


    await state.set_state(
        FilmCreation.camera
    )


    await message.answer(
        "На что снимаем?\n\n"
        "Если ничего не указать — считаем iPhone."
    )



# =========================
# CAMERA + GENERATION
# =========================

@dp.message(FilmCreation.camera)
async def generate(
    message: Message,
    state:FSMContext
):

    await state.update_data(
        camera=message.text
    )


    data = await state.get_data()


    await message.answer(
        "🎬 Создаю режиссерский пакет фильма..."
    )


    prompt=f"""

Создай фильм.

Идея:
{data['idea']}

Жанр:
{data['genre']}

Главный герой:
{data['hero']}

Формат:
{data['format']}

Камера:
{data['camera']}


Создай подробный план съемки.
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

            temperature=0.8,
            max_tokens=5000
        )


        await message.answer(
            response.choices[0].message.content
        )


    except Exception as e:

        await message.answer(
            f"Ошибка:\n{e}"
        )


    await state.clear()



# =========================

async def main():

    print("ReelCinema AI запущен")

    await dp.start_polling(bot)



if __name__=="__main__":

    asyncio.run(main())