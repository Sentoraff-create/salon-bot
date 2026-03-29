import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from database import init_database
from handlers import router
from admin import admin_router
from reminders import start_reminders

logging.basicConfig(level=logging.INFO)

async def main():
    print("=" * 45)
    print(" БОТ ДЛЯ ПАРИКМАХЕРСКОЙ ЗАПУСКАЕТСЯ...")
    print("=" * 45)

    init_database()
    print(" База данных: OK")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(admin_router)
    task = asyncio.create_task(start_reminders(bot))

    print(" Напоминания: OK")
    print("=" * 45)
    print(" БОТ РАБОТАЕТ! ")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        print(" Бот остановлен")
