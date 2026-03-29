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
    print("=" * 50)
    print(" БОТ ДЛЯ ПАРИКМАХЕРСКОЙ ЗАПУСКАЕТСЯ...")
    print("=" * 50)

    init_database()
    print(" База данных: OK")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(admin_router)

    # Запуск напоминаний в фоне
    asyncio.create_task(start_reminders(bot))

    print(" Напоминания запущены")
    print("=" * 50)
    print(" БОТ ЗАПУЩЕН В РЕЖИМЕ POLLING")
    print(" Ожидаем сообщения от пользователей...")

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
    finally:
        await bot.session.close()
        print("🛑 Бот остановлен")
