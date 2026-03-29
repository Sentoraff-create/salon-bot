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
    print("=" * 60)
    print("МИНИМАЛЬНЫЙ ТЕСТОВЫЙ БОТ")
    print("=" * 60)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    print("✅ Бот и Dispatcher созданы")
    print("🚀 Бот запущен в режиме polling")
    print("Напиши сообщение боту в Telegram...")

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()
        print("🛑 Бот остановлен")

if name == "__main__":
    asyncio.run(main())
