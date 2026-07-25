import os
import asyncio

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

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



SYSTEM_PROMPT = """
Ты — профессиональный режиссер рекламы, кино и коротких видео.

Ты помогаешь создавать:
- Reels
- TikTok
- YouTube Shorts
- рекламные ролики
- кинематографичные сцены

Отвечай как режиссер-постановщик.

Учитывай:
- сильный хук первых секунд
- драматургию
- композицию кадра
- движение камеры
- свет
- звук
- монтаж

Если пользователь дает идею — развивай её в полноценный съемочный план.

Структура ответа:

🔥 Хук

🎬 Сценарий

📷 Раскадровка

🎥 Камера и объектив

💡 Свет

🎙 Звук

🎞 Монтаж

Не давай общих советов. Давай конкретные решения для съемки.
"""


@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "🎬 ReelCinema AI\n\n"
        "Я твой виртуальный режиссер.\n\n"
        "Опиши идею ролика, сцену или задачу — "
        "и я помогу её снять."
    )



@dp.message(F.text)
async def generate(message: Message):

    try:

        await message.answer(
            "🎬 Думаю как режиссер..."
        )


        response = await client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message.text
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
            f"Ошибка генерации:\n{e}"
        )



async def main():

    print("ReelCinema AI запущен")

    await dp.start_polling(bot)



if __name__ == "__main__":

    asyncio.run(main())