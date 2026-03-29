import asyncio
import logging
from database import get_pending_reminders, mark_reminder

logger = logging.getLogger(__name__)

async def start_reminders(bot):
    while True:
        try:
            r24, r1 = get_pending_reminders()
            for b in r24:
                try:
                    await bot.send_message(b['telegram_id'],
                        f"🔔 Напоминание!\n\nЗавтра у вас запись:\n"
                        f"💈 {b['service_name']}\n✂️ Мастер: {b['master_name']}\n🕐 Время: {b['time']}")
                    mark_reminder(b['id'], "24h")
                except:
                    pass
            for b in r1:
                try:
                    await bot.send_message(b['telegram_id'],
                        f"⏰ Через 1 час ваша запись!\n"
                        f"💈 {b['service_name']}\n✂️ {b['master_name']}\n🕐 {b['time']}")
                    mark_reminder(b['id'], "1h")
                except:
                    pass
        except Exception as e:
            logger.error(f"Ошибка напоминаний: {e}")
        await asyncio.sleep(300)
