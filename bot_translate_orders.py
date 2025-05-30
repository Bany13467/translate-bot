import asyncio
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from googletrans import Translator

# 🔐 Твои данные:
BOT_TOKEN = "7817323682:AAGKPcuW3sp1OVLC2OiD1ypThFIbkWslX64"
USER_ID = 6058368718  # твой Telegram ID

# Настройка бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()
translator = Translator()

URL = "https://kwork.ru/projects?category=переводы"
sent_titles = set()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("✅ Бот запущен! Я буду искать заказы на перевод и присылать переведённые заголовки.")


async def check_orders():
    global sent_titles
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        projects = soup.select("div.wants-card__header-title > a")

        new_orders = []
        for project in projects:
            title = project.get_text(strip=True)
            link = "https://kwork.ru" + project["href"]
            if title not in sent_titles:
                translated = translator.translate(title, src="en", dest="ru").text
                new_orders.append(f"🆕 <b>{title}</b>\n🔗 {link}\n\n🌐 Перевод:\n{translated}")
                sent_titles.add(title)

        if new_orders:
            msg = "\n\n".join(new_orders[:5])
            await bot.send_message(USER_ID, msg)

    except Exception as e:
        print("❌ Ошибка при парсинге:", e)


async def background_task():
    while True:
        await check_orders()
        await asyncio.sleep(60)  # каждые 60 секунд


async def main():
    dp.include_router(router)
    asyncio.create_task(background_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
