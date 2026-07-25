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
# ПАМЯТЬ
# =========================

users_started = set()

chat_memory = {}


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
Ты — профессиональный режиссер, оператор-постановщик и монтажер.

Ты помогаешь создавать:
- Reels
- TikTok
- Shorts
- рекламные ролики
- киношные сцены
- YouTube видео

По умолчанию считай:
Съемка идет на iPhone.
Если пользователь указал другую камеру — используй её.

Твоя задача:
Давать конкретный план действий для съемки.

Не просто придумывай идею.
Объясняй, как это реально снять.

Структура ответа:

🎯 ЦЕЛЬ
Что должно получиться.

🔥 ХУК (первые 3 секунды)
Что сразу цепляет зрителя.

🎬 СЦЕНАРИЙ
Пошагово:
- действие
- эмоция
- развитие

📱 СЪЕМКА
Укажи:
- настройки iPhone
- положение камеры
- расстояние
- движение камеры
- свет

📷 КАДРЫ

Кадр 1:
План:
Что происходит:

Кадр 2:
План:
Что происходит:

🎙 ЗВУК

🎞 МОНТАЖ

Всегда думай как режиссер на площадке.
Не пиши общие советы.
Давай конкретные действия.
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
            "🎬 Добро пожаловать в ReelCinema AI.\n\n"
            "Я твой виртуальный режиссер.\n\n"
            "Помогу превратить идею в готовый план съемки:\n"
            "🎥 сценарий\n"
            "📷 кадры\n"
            "💡 свет\n"
            "🎙 звук\n"
            "🎞 монтаж\n\n"
            "По умолчанию считаем, что съемка идет на iPhone.\n\n"
            "Расскажи свою идею 👇"
        )

    else:

        await message.answer(
            "🎬 ReelCinema AI снова готов.\n"
            "Продолжаем работу 👇"
        )



# =========================
# CHAT
# =========================

@dp.message(F.text)
async def chat(message: Message):

    user_id = message.from_user.id

    user_text = message.text


    if user_id not in chat_memory:
        chat_memory[user_id] = []


    chat_memory[user_id].append(
        {
            "role": "user",
            "content": user_text
        }
    )


    # оставляем последние 10 сообщений
    history = chat_memory[user_id][-10:]


    try:

        response = await client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ] + history,

            temperature=0.7,
            max_tokens=3000
        )


        answer = response.choices[0].message.content


        chat_memory[user_id].append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        await message.answer(answer)


    except Exception as e:

        await message.answer(
            f"Ошибка генерации:\n{e}"
        )


# =========================
# RUN
# =========================

async def main():

    print("ReelCinema AI запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())