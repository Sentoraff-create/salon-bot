from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SALON_NAME, SALON_PHONE, SALON_ADDRESS, ADMIN_ID
from database import (get_or_create_client, get_masters, get_services,
                      create_booking, get_client_bookings, cancel_booking, save_review)
from keyboards import (main_menu, back, masters_kb, services_kb, dates_kb,
                       times_kb, confirm_kb, bookings_kb, rating_kb)

router = Router()

class Book(StatesGroup):
    svc = State()
    master = State()
    date = State()
    time = State()
    confirm = State()

class Review(StatesGroup):
    rating = State()
    comment = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    get_or_create_client(message.from_user.id, message.from_user.full_name)
    await message.answer(
        f"👋 Добро пожаловать в {SALON_NAME}!\n\n"
        f"Здесь вы можете:\n"
        f"📝 Записаться на услугу\n"
        f"💈 Посмотреть цены\n"
        f"📅 Управлять своими записями\n\n"
        f"Выберите действие:",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "main")
async def go_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"🏠 {SALON_NAME} — Главное меню\n\nВыберите действие:",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "services")
async def show_services(callback: CallbackQuery):
    svcs = get_services()
    text = "💈 Наши услуги и цены:\n\n"
    for s in svcs:
        text += f"• {s['name']} — {s['price']} руб ({s['duration']} мин)\n"
    await callback.message.edit_text(text, reply_markup=back())

@router.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    await callback.message.edit_text(
        f"📞 Контакты {SALON_NAME}\n\n"
        f"📱 Телефон: {SALON_PHONE}\n"
        f"📍 Адрес: {SALON_ADDRESS}\n"
        f"🕐 Работаем: 09:00 — 20:00",
        reply_markup=back()
    )

@router.callback_query(F.data == "promos")
async def show_promos(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎁 Наши акции:\n\n"
        "🔥 Скидка 20% на первое посещение!\n"
        "🎂 Скидка 15% в день рождения\n"
        "👥 Приведи друга — скидка 10%\n\n"
        "Записывайтесь прямо сейчас!",
        reply_markup=back()
    )

@router.callback_query(F.data == "book")
async def start_book(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Book.svc)
    await callback.message.edit_text(
        "📝 Запись — Шаг 1 из 4\n\n💈 Выберите услугу:",
        reply_markup=services_kb(get_services(), booking=True)
    )

@router.callback_query(Book.svc, F.data.startswith("svc_"))
async def pick_svc(callback: CallbackQuery, state: FSMContext):
    svc_id = int(callback.data.split("_")[1])
    await state.update_data(svc_id=svc_id)
    await state.set_state(Book.master)
    await callback.message.edit_text(
        "📝 Запись — Шаг 2 из 4\n\n✂️ Выберите мастера:",
        reply_markup=masters_kb(get_masters())
    )

@router.callback_query(Book.master, F.data.startswith("master_"))
async def pick_master(callback: CallbackQuery, state: FSMContext):
    master_id = int(callback.data.split("_")[1])
    await state.update_data(master_id=master_id)
    await state.set_state(Book.date)
    await callback.message.edit_text(
        "📝 Запись — Шаг 3 из 4\n\n📅 Выберите дату:",
        reply_markup=dates_kb()
    )

@router.callback_query(Book.date, F.data.startswith("date_"))
async def pick_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    await state.update_data(date=date)
    await state.set_state(Book.time)
    await callback.message.edit_text(
        "📝 Запись — Шаг 4 из 4\n\n🕐 Выберите время:",
        reply_markup=times_kb()
    )

@router.callback_query(Book.time, F.data.startswith("time_"))
async def pick_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split("_")[1]
    await state.update_data(time=time)
    data = await state.get_data()

    svcs = {s['id']: s for s in get_services()}
    masters = {m['id']: m for m in get_masters()}
    svc = svcs[data['svc_id']]
    master = masters[data['master_id']]

    await state.set_state(Book.confirm)
    await callback.message.edit_text(
        f"✅ Проверьте вашу запись:\n\n"
        f"💈 Услуга: {svc['name']}\n"
        f"💰 Цена: {svc['price']} руб\n"
        f"✂️ Мастер: {master['name']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n\n"
        f"Всё верно?",
        reply_markup=confirm_kb()
    )

@router.callback_query(Book.confirm, F.data == "confirm")
async def do_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    client = get_or_create_client(callback.from_user.id, callback.from_user.full_name)
    bid = create_booking(client['id'], data['master_id'], data['svc_id'], data['date'], data['time'])
    await state.clear()

    svcs = {s['id']: s for s in get_services()}
    masters = {m['id']: m for m in get_masters()}
    svc = svcs[data['svc_id']]
    master = masters[data['master_id']]

    await callback.message.edit_text(
        f"🎉 Запись создана! Номер: #{bid}\n\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"✂️ Мастер: {master['name']}\n\n"
        f"Мы напомним вам за 24 часа и за 1 час!",
        reply_markup=back()
    )
    try:
        await callback.bot.send_message(
            ADMIN_ID,
            f"🔔 Новая запись #{bid}!\n"
            f"👤 Клиент: {callback.from_user.full_name}\n"
            f"💈 Услуга: {svc['name']}\n"
            f"✂️ Мастер: {master['name']}\n"
            f"📅 {data['date']} в {data['time']}"
        )
    except:
        pass

@router.callback_query(F.data == "my_bookings")
async def my_bookings(callback: CallbackQuery):
    client = get_or_create_client(callback.from_user.id, callback.from_user.full_name)
    bks = get_client_bookings(client['id'])
    if not bks:
        await callback.message.edit_text(
            "У вас нет активных записей.\n\nЗапишитесь прямо сейчас!",
            reply_markup=back()
        )
        return
    text = "📅 Ваши записи:\n\n"
    for b in bks:
        text += f"• {b['date']} {b['time']} — {b['service_name']} ({b['master_name']})\n"
    await callback.message.edit_text(text, reply_markup=bookings_kb(bks))

@router.callback_query(F.data.startswith("cancel_"))
async def do_cancel(callback: CallbackQuery):
    bid = int(callback.data.split("_")[1])
    client = get_or_create_client(callback.from_user.id, callback.from_user.full_name)
    cancel_booking(bid, client['id'])
    await callback.message.edit_text("✅ Запись отменена.", reply_markup=back())
