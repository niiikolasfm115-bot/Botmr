"""
Database helpers for the OTP bot using sqlite3.
Provides init_db() and basic CRUD helpers used by handlers.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Tuple

DB_PATH = os.getenv("DB_PATH", "bot1.db")

def init_db(db_path: Optional[str] = None):
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            country_code TEXT,
            assigned_number TEXT,
            is_banned INTEGER DEFAULT 0,
            private_combo_country TEXT DEFAULT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS combos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            combo_index INTEGER DEFAULT 1,
            numbers TEXT,
            UNIQUE(country_code, combo_index)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            otp TEXT,
            full_message TEXT,
            timestamp TEXT,
            assigned_to INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS private_combos (
            user_id INTEGER,
            country_code TEXT,
            numbers TEXT,
            PRIMARY KEY (user_id, country_code)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS force_sub_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_url TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# Basic helpers

def get_setting(key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_setting(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def save_user(user_id: int, username: str = "", first_name: str = "", last_name: str = "", country_code: Optional[str] = None, assigned_number: Optional[str] = None, private_combo_country: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # preserve existing fields if None
    c.execute("SELECT country_code, assigned_number, private_combo_country FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        if country_code is None:
            country_code = row[0]
        if assigned_number is None:
            assigned_number = row[1]
        if private_combo_country is None:
            private_combo_country = row[2]
    c.execute("REPLACE INTO users (user_id, username, first_name, last_name, country_code, assigned_number, is_banned, private_combo_country) VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id=?), 0), ?)",
              (user_id, username, first_name, last_name, country_code, assigned_number, user_id, private_combo_country))
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def is_banned(user_id: int) -> bool:
    user = get_user(user_id)
    return bool(user and user[6] == 1)


def get_all_combos() -> List[Tuple[str, int]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT country_code, combo_index FROM combos ORDER BY country_code, combo_index")
    combos = c.fetchall()
    conn.close()
    return combos


def get_combo(country_code: str, combo_index: int = 1, user_id: Optional[int] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("SELECT numbers FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
        row = c.fetchone()
        if row:
            conn.close()
            return json.loads(row[0])
    c.execute("SELECT numbers FROM combos WHERE country_code=? AND combo_index=?", (country_code, combo_index))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []


def save_combo(country_code: str, numbers: list, user_id: Optional[int] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id:
        c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?, ?, ?)", (user_id, country_code, json.dumps(numbers)))
    else:
        c.execute("SELECT MAX(combo_index) FROM combos WHERE country_code=?", (country_code,))
        max_index = c.fetchone()[0]
        next_index = 1 if max_index is None else max_index + 1
        c.execute("INSERT INTO combos (country_code, combo_index, numbers) VALUES (?, ?, ?)", (country_code, next_index, json.dumps(numbers)))
    conn.commit()
    conn.close()


def assign_number_to_user(user_id: int, number: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
    conn.commit()
    conn.close()


def release_number(old_number: str):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()


def log_otp(number: str, otp: str, full_message: str, assigned_to: Optional[int] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (number, otp, full_message, timestamp, assigned_to) VALUES (?, ?, ?, ?, ?)", (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
    conn.commit()
    conn.close()
