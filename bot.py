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

dp = Dispatcher(
    storage=MemoryStorage()
)


# =========================
# FSM STATES
# =========================

class FilmCreation(StatesGroup):
    idea = State()
    genre = State()
    hero = State()
    format = State()
    camera = State()


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """

Ты — ReelCinema AI.
Ты профессиональный режиссер, сценарист и оператор-постановщик.

Твоя задача — помочь новичку снять настоящий фильм самостоятельно.

По умолчанию съемка идет на iPhone.

Создай подробный режиссерский пакет:

🎬 НАЗВАНИЕ ФИЛЬМА

🎭 ЖАНР

📝 ЛОГЛАЙН

Короткая идея фильма.


👤 ГЛАВНЫЙ ГЕРОЙ

Кто он.
Чего хочет.
Чего боится.
Его внутренний конфликт.


🎞 СТРУКТУРА

Акт 1:
Завязка.

Акт 2:
Конфликт.

Акт 3:
Развязка.


🎬 СЦЕНЫ

Для каждой сцены:

Название:

Локация:

Задача сцены:

Эмоция:


КАДРЫ:

Кадр 1:
- план
- фокусное расстояние
- положение камеры
- движение камеры
- композиция
- свет
- звук


Кадр 2:
...


🎥 ОПЕРАТОРСКОЕ РЕШЕНИЕ

Объясни:
- почему выбран такой кадр
- как создать эмоцию
- как удерживать внимание зрителя


✂️ МОНТАЖ

Укажи:
- темп
- паузы
- переходы
- усиление напряжения


🔊 ЗВУК

Укажи:
- музыку
- шумы
- атмосферу


🎯 УДЕРЖАНИЕ ЗРИТЕЛЯ

Объясни:
- какой вопрос должен возникнуть у зрителя
- где раскрывать информацию
- где делать поворот


Пиши как настоящий режиссер.
Не давай общих советов.
Давай конкретный план съемки.
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
        "Я помогу превратить твою идею в настоящий фильм.\n\n"
        "Мы создадим:\n"
        "🎭 историю\n"
        "🎬 сцены\n"
        "📷 кадры\n"
        "💡 свет\n"
        "🔊 звук\n"
        "✂️ монтаж\n\n"
        "По умолчанию снимаем на iPhone.\n\n"
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

    print("IDEA:", message.text)

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
        "драма\n"
        "хоррор\n"
        "триллер\n"
        "фантастика"
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

    await state.update_data(
        camera=message.text
    )

    data = await state.get_data()

    await message.answer(
        "🎬 Создаю режиссерский пакет фильма..."
    )

    prompt = f"""

Создай фильм.

Идея:
{data.get('idea')}

Жанр:
{data.get('genre')}

Главный герой:
{data.get('hero')}

Формат:
{data.get('format')}

Камера:
{data.get('camera')}

Сделай подробный съемочный план.
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
            max_tokens=4500
        )


        answer = response.choices[0].message.content


        for i in range(0, len(answer), 4000):
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

    print("ReelCinema AI запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())