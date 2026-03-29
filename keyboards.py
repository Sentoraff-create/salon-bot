from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записаться на услугу", callback_data="book")],
        [InlineKeyboardButton(text="💈 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton(text="📅 Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="📞 Контакты салона", callback_data="contacts")],
        [InlineKeyboardButton(text="🎁 Акции и скидки", callback_data="promos")],
    ])

def back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main")]
    ])

def masters_kb(masters):
    rows = [[InlineKeyboardButton(text=f"✂️ {m['name']} — {m['specialty']}", callback_data=f"master_{m['id']}")] for m in masters]
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def services_kb(services, booking=False):
    rows = []
    for s in services:
        if booking:
            rows.append([InlineKeyboardButton(text=f"{s['name']} — {s['price']} руб ({s['duration']} мин)", callback_data=f"svc_{s['id']}")])
        else:
            rows.append([InlineKeyboardButton(text=f"💈 {s['name']} — {s['price']} руб", callback_data=f"svcinfo_{s['id']}")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def dates_kb():
    rows = []
    days = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    for i in range(14):
        d = datetime.now() + timedelta(days=i)
        rows.append([InlineKeyboardButton(
            text=f"{days[d.weekday()]}  {d.strftime('%d.%m.%Y')}",
            callback_data=f"date_{d.strftime('%Y-%m-%d')}"
        )])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def times_kb():
    times = ["09:00","10:00","11:00","12:00","14:00","15:00","16:00","17:00","18:00","19:00"]
    rows = []
    row = []
    for i, t in enumerate(times):
        row.append(InlineKeyboardButton(text=t, callback_data=f"time_{t}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить запись", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="main")],
    ])

def bookings_kb(bookings):
    rows = []
    for b in bookings:
        rows.append([InlineKeyboardButton(
            text=f"❌ Отменить {b['date']} {b['time']} — {b['service_name']}",
            callback_data=f"cancel_{b['id']}"
        )])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def rating_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 1", callback_data="rating_1"),
            InlineKeyboardButton(text="⭐⭐ 2", callback_data="rating_2"),
            InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data="rating_3"),
        ],
        [
            InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data="rating_4"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data="rating_5"),
        ],
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Все записи", callback_data="adm_bookings")],
        [InlineKeyboardButton(text="👥 Все клиенты", callback_data="adm_clients")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast")],
    ])
