import streamlit as st
import sqlite3
import os
from datetime import datetime, date

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

# ========== Additional Functions for Dashboard ==========

def get_todays_total_expense():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (today,))
    result = c.fetchone()[0]
    conn.close()
    return result or 0.0

def get_monthly_deposits():
    today = date.today()
    first_day = today.replace(day=1).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT SUM(amount) FROM deposits 
        WHERE date BETWEEN ? AND ?
    """, (first_day, today_str))
    result = c.fetchone()[0]
    conn.close()
    return result or 0.0

# ========== Deposit operations ==========

def add_deposit(roommate, amount, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO deposits (roommate, amount, date) VALUES (?, ?, ?)",
        (roommate, amount, date),
    )
    conn.commit()
    conn.close()

def get_deposits():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT roommate, amount, date FROM deposits ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ========== Streamlit app ==========

# Custom rerun function compatible with Streamlit 1.45.1+
def rerun():
    import streamlit.runtime.scriptrunner as scriptrunner
    raise scriptrunner.RerunException(scriptrunner.RerunData())

st.title("🏠 Roommate Expense Manager")

menu = ["Dashboard", "View Roommates", "Add Roommate", "Remove Roommate", "Add Expense", "View Today's Expenses"]
menu.append("Add Deposit")
menu.append("View Deposits")

choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.subheader("📊 Overview (Today's Summary)")

    total_expense_today = get_todays_total_expense()
    total_deposits = get_monthly_deposits()
    remaining = total_deposits - total_expense_today

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Today's Expenses", f"₹{total_expense_today:.2f}")
    col2.metric("💰 Deposits (1st–Today)", f"₹{total_deposits:.2f}")
    col3.metric("🧾 Remaining Balance", f"₹{remaining:.2f}")

elif choice == "View Roommates":
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
        date_val = st.date_input("Date", value=datetime.now())
        description = st.text_area("Description")
        if st.button("Add Expense"):
            add_expense(selected, amount, date_val.strftime("%Y-%m-%d"), description)
            st.success("Expense added successfully.")
            rerun()

elif choice == "View Today's Expenses":
    st.subheader("Today's Expenses")
    expenses = get_todays_expenses()
    if expenses:
        for roommate, amount, desc in expenses:
            st.write(f"- {roommate} paid ₹{amount:.2f} for {desc}")
    else:
        st.info("No expenses recorded for today.")

elif choice == "Add Deposit":
    st.subheader("Add Deposit")
    roommates = get_roommates()
    if not roommates:
        st.warning("Add roommates before adding deposits.")
    else:
        selected = st.selectbox("Select Roommate", roommates)
        amount = st.number_input("Deposit Amount", min_value=0.01, format="%.2f")
        date_val = st.date_input("Date", value=datetime.now())
        if st.button("Add Deposit"):
            add_deposit(selected, amount, date_val.strftime("%Y-%m-%d"))
            st.success(f"Deposit of ₹{amount:.2f} added for {selected}.")
            rerun()

elif choice == "View Deposits":
    st.subheader("All Deposits")
    deposits = get_deposits()
    if deposits:
        for roommate, amount, d in deposits:
            st.write(f"- {roommate} deposited ₹{amount:.2f} on {d}")
    else:
        st.info("No deposits recorded yet.")
