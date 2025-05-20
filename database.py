import sqlite3
import os

def get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
    return sqlite3.connect("data/roommates.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roommates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_by TEXT NOT NULL,
            description TEXT
        )
    ''')

    conn.commit()
    conn.close()
