from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database import get_all_bookings, get_all_clients
from keyboards import admin_kb, back

admin_router = Router()

class Broadcast(StatesGroup):
    msg = State()

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return
    await message.answer("👑 Панель администратора:", reply_markup=admin_kb())

@admin_router.callback_query(F.data == "adm_bookings")
async def adm_bookings(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    bks = get_all_bookings()
    if not bks:
        await callback.message.edit_text("Записей нет.", reply_markup=back())
        return
    text = f"📅 Записей всего: {len(bks)}\n\n"
    for b in bks[:15]:
        text += f"• {b['date']} {b['time']} | {b['client_name']} | {b['service_name']} | {b['master_name']}\n"
    await callback.message.edit_text(text, reply_markup=back())

@admin_router.callback_query(F.data == "adm_clients")
async def adm_clients(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    clients = get_all_clients()
    text = f"👥 Клиентов: {len(clients)}\n\n"
    for c in clients[:20]:
        text += f"• {c['name']}\n"
    await callback.message.edit_text(text, reply_markup=back())

@admin_router.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(Broadcast.msg)
    await callback.message.edit_text(
        "📢 Введите текст рассылки для всех клиентов:",
        reply_markup=back()
    )

@admin_router.message(Broadcast.msg)
async def do_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    clients = get_all_clients()
    sent = 0
    for c in clients:
        try:
            await message.bot.send_message(c['telegram_id'], f"📢 {message.text}")
            sent += 1
        except:
            pass
    await state.clear()
    await message.answer(f"Рассылка отправлена {sent} клиентам!")
