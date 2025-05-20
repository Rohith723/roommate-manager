import streamlit as st
import sqlite3
import os
from datetime import datetime

# ========== Database setup ==========

DB_PATH = "data/roommates.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS roommates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roommate TEXT,
            amount REAL,
            date TEXT,
            description TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            roommate TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

create_tables()

# ========== DB Operations ==========

def add_roommate(name):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO roommates (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning(f"Roommate '{name}' already exists.")
    finally:
        conn.close()

def remove_roommate(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM roommates WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def get_roommates():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM roommates")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_expense(roommate, amount, date, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (roommate, amount, date, description) VALUES (?, ?, ?, ?)",
        (roommate, amount, date, description),
    )
    conn.commit()
    conn.close()

def get_todays_expenses():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT roommate, amount, description FROM expenses WHERE date = ?", (today,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

# ========== Streamlit app ==========

# Custom rerun function compatible with Streamlit 1.45.1+
def rerun():
    import streamlit.runtime.scriptrunner as scriptrunner
    raise scriptrunner.RerunException(scriptrunner.RerunData())

st.title("🏠 Roommate Expense Manager")

menu = ["View Roommates", "Add Roommate", "Remove Roommate", "Add Expense", "View Today's Expenses"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "View Roommates":
    st.subheader("Roommates List")
    roommates = get_roommates()
    if roommates:
        for mate in roommates:
            st.write(f"- {mate}")
    else:
        st.info("No roommates added yet.")

elif choice == "Add Roommate":
    st.subheader("Add New Roommate")
    new_name = st.text_input("Roommate Name")
    if st.button("Add") and new_name.strip():
        add_roommate(new_name.strip())
        st.success(f"Roommate '{new_name.strip()}' added.")
        rerun()

elif choice == "Remove Roommate":
    st.subheader("Remove Roommate")
    roommates = get_roommates()
    if roommates:
        selected = st.selectbox("Select roommate to remove", roommates)
        if st.button("Remove"):
            remove_roommate(selected)
            st.warning(f"Roommate '{selected}' removed.")
            rerun()
    else:
        st.info("No roommates to remove.")

elif choice == "Add Expense":
    st.subheader("Add Expense")
    roommates = get_roommates()
    if not roommates:
        st.warning("Add roommates before adding expenses.")
    else:
        selected = st.selectbox("Select Roommate", roommates)
        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        date = st.date_input("Date", value=datetime.now())
        description = st.text_area("Description")
        if st.button("Add Expense"):
            add_expense(selected, amount, date.strftime("%Y-%m-%d"), description)
            st.success("Expense added successfully.")
            rerun()

elif choice == "View Today's Expenses":
    st.subheader("Today's Expenses")
    expenses = get_todays_expenses()
    if expenses:
        for roommate, amount, desc in expenses:
            st.write(f"- {roommate} paid ${amount:.2f} for {desc}")
    else:
        st.info("No expenses recorded for today.")

