import sqlite3
from datetime import datetime, timedelta

DB = "salon.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    c = db()
    cur = c.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS masters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specialty TEXT,
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            duration INTEGER,
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            master_id INTEGER,
            service_id INTEGER,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'confirmed',
            reminder_24h INTEGER DEFAULT 0,
            reminder_1h INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("SELECT COUNT(*) FROM masters")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO masters (name, specialty) VALUES (?,?)", [
            ("Анна", "Стрижки и укладки"),
            ("Мария", "Окраска волос"),
            ("Елена", "Все виды услуг"),
        ])
    cur.execute("SELECT COUNT(*) FROM services")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO services (name, price, duration) VALUES (?,?,?)", [
            ("Мужская стрижка", 800, 45),
            ("Женская стрижка", 1200, 60),
            ("Окраска волос", 2500, 120),
            ("Укладка", 800, 45),
            ("Химическая завивка", 3000, 150),
            ("Маникюр", 1000, 60),
        ])
    c.commit()
    c.close()

def get_or_create_client(telegram_id, name):
    c = db()
    cur = c.cursor()
    cur.execute("SELECT * FROM clients WHERE telegram_id=?", (telegram_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO clients (telegram_id, name) VALUES (?,?)", (telegram_id, name))
        c.commit()
        cur.execute("SELECT * FROM clients WHERE telegram_id=?", (telegram_id,))
        row = cur.fetchone()
    c.close()
    return dict(row)

def get_masters():
    c = db()
    cur = c.cursor()
    cur.execute("SELECT * FROM masters WHERE is_active=1")
    rows = [dict(r) for r in cur.fetchall()]
    c.close()
    return rows

def get_services():
    c = db()
    cur = c.cursor()
    cur.execute("SELECT * FROM services WHERE is_active=1")
    rows = [dict(r) for r in cur.fetchall()]
    c.close()
    return rows

def create_booking(client_id, master_id, service_id, date, time):
    c = db()
    cur = c.cursor()
    cur.execute("INSERT INTO bookings (client_id,master_id,service_id,date,time) VALUES (?,?,?,?,?)",
                (client_id, master_id, service_id, date, time))
    bid = cur.lastrowid
    c.commit()
    c.close()
    return bid

def get_client_bookings(client_id):
    c = db()
    cur = c.cursor()
    cur.execute("""
        SELECT b.*, m.name as master_name, s.name as service_name, s.price
        FROM bookings b
        JOIN masters m ON b.master_id=m.id
        JOIN services s ON b.service_id=s.id
        WHERE b.client_id=? AND b.status!='cancelled'
        ORDER BY b.date, b.time
    """, (client_id,))
    rows = [dict(r) for r in cur.fetchall()]
    c.close()
    return rows

def cancel_booking(booking_id, client_id):
    c = db()
    cur = c.cursor()
    cur.execute("UPDATE bookings SET status='cancelled' WHERE id=? AND client_id=?", (booking_id, client_id))
    c.commit()
    c.close()

def get_all_bookings():
    c = db()
    cur = c.cursor()
    cur.execute("""
        SELECT b.*, c.name as client_name, c.telegram_id,
               m.name as master_name, s.name as service_name, s.price
        FROM bookings b
        JOIN clients c ON b.client_id=c.id
        JOIN masters m ON b.master_id=m.id
        JOIN services s ON b.service_id=s.id
        WHERE b.status!='cancelled'
        ORDER BY b.date, b.time
    """)
    rows = [dict(r) for r in cur.fetchall()]
    c.close()
    return rows

def get_all_clients():
    c = db()
    cur = c.cursor()
    cur.execute("SELECT * FROM clients")
    rows = [dict(r) for r in cur.fetchall()]
    c.close()
    return rows

def save_review(client_id, rating, comment):
    c = db()
    cur = c.cursor()
    cur.execute("INSERT INTO reviews (client_id,rating,comment) VALUES (?,?,?)", (client_id, rating, comment))
    c.commit()
    c.close()

def get_pending_reminders():
    c = db()
    cur = c.cursor()
    now = datetime.now()
    tomorrow = (now + timedelta(hours=24)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT b.*, c.telegram_id, m.name as master_name, s.name as service_name
        FROM bookings b JOIN clients c ON b.client_id=c.id
        JOIN masters m ON b.master_id=m.id JOIN services s ON b.service_id=s.id
        WHERE b.status='confirmed' AND b.reminder_24h=0 AND b.date=?
    """, (tomorrow,))
    r24 = [dict(r) for r in cur.fetchall()]
    soon = (now + timedelta(hours=1)).strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")
    cur.execute("""
        SELECT b.*, c.telegram_id, m.name as master_name, s.name as service_name
        FROM bookings b JOIN clients c ON b.client_id=c.id
        JOIN masters m ON b.master_id=m.id JOIN services s ON b.service_id=s.id
        WHERE b.status='confirmed' AND b.reminder_1h=0 AND b.date=? AND b.time=?
    """, (today, soon))
    r1 = [dict(r) for r in cur.fetchall()]
    c.close()
    return r24, r1

def mark_reminder(booking_id, t):
    c = db()
    cur = c.cursor()
    field = "reminder_24h" if t == "24h" else "reminder_1h"
    cur.execute(f"UPDATE bookings SET {field}=1 WHERE id=?", (booking_id,))
    c.commit()
    c.close()
