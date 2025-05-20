import sqlite3
import os

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect("data/roommates.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS roommates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roommate TEXT,
        amount REAL,
        date TEXT,
        description TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        roommate TEXT,
        date TEXT
    )''')

    conn.commit()
    conn.close()

def add_roommate(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO roommates (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_roommates():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM roommates")
    data = c.fetchall()
    conn.close()
    return [d[0] for d in data]

def remove_roommate(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM roommates WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def add_expense(roommate, amount, date, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO expenses (roommate, amount, date, description) VALUES (?, ?, ?, ?)",(roommate, amount, date, description))
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM expenses")
    data = c.fetchall()
    conn.close()
    return data

def add_deposit(amount, roommate, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO deposits (amount, roommate, date) VALUES (?, ?, ?)", (amount, roommate, date))
    conn.commit()
    conn.close()

def get_all_deposits():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM deposits")
    data = c.fetchall()
    conn.close()
    return data
