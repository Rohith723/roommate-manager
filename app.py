# roommate_expense_manager/app.py

import streamlit as st
import sqlite3
import os
from datetime import datetime, date

# Database setup
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

create_tables()

# Data functions
def add_roommate(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO roommates (name) VALUES (?)", (name,))
    conn.commit()
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
    c.execute("INSERT INTO expenses (roommate, amount, date, description) VALUES (?, ?, ?, ?)",
              (roommate, amount, date, description))
    conn.commit()
    conn.close()

def get_todays_expenses():
    conn = get_connection()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("SELECT roommate, amount, description FROM expenses WHERE date = ?", (today,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_total_expenses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses")
    total = c.fetchone()[0]
    conn.close()
    return total or 0

def add_deposit(amount, roommate, deposit_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO deposits (amount, roommate, date) VALUES (?, ?, ?)",
              (amount, roommate, deposit_date))
    conn.commit()
    conn.close()

def get_total_deposits():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM deposits")
    total = c.fetchone()[0]
    conn.close()
    return total or 0

# Streamlit UI
st.set_page_config(page_title="Roommate Expense Manager", layout="centered")
st.title("🏡 BADCOWS ")

menu = ["Home", "Add Roommate", "Add Expense", "Add Deposit", "Remove Roommate"]
choice = st.sidebar.selectbox("Navigate", menu)

if choice == "Home":
    st.subheader("📅 Today's Expenses")
    expenses = get_todays_expenses()
    if expenses:
        for roommate, amount, desc in expenses:
            st.write(f"**{roommate}** spent **₹{amount}** for _{desc}_")
    else:
        st.info("No expenses recorded today.")

    st.subheader("💳 Summary")
    total_exp = get_total_expenses()
    total_dep = get_total_deposits()
    remaining = total_dep - total_exp

    st.write(f"**Total Expenses:** ₹{total_exp}")
    st.write(f"**Total Deposits:** ₹{total_dep}")
    st.write(f"**Remaining Balance:** ₹{remaining}")

    st.subheader("👥 Roommates")
    roommates = get_roommates()
    st.write(", ".join(roommates) if roommates else "No roommates added yet.")

elif choice == "Add Roommate":
    st.subheader("➕ Add Roommate")
    new_mate = st.text_input("Roommate Name")
    if st.button("Add") and new_mate:
        add_roommate(new_mate)
        st.success(f"Roommate '{new_mate}' added.")
        st.experimental_rerun()

elif choice == "Add Expense":
    st.subheader("➖ Add Expense")
    mates = get_roommates()
    if mates:
        selected = st.selectbox("Select Roommate", mates)
        amount = st.number_input("Amount", min_value=1.0, step=1.0)
        desc = st.text_input("Description")
        today = date.today().isoformat()
        if st.button("Submit"):
            add_expense(selected, amount, today, desc)
            st.success("Expense added!")
            st.experimental_rerun()
    else:
        st.warning("Please add roommates first.")

elif choice == "Add Deposit":
    st.subheader("📅 Add Deposit")
    mates = get_roommates()
    if mates:
        selected = st.selectbox("Select Roommate", mates)
        amount = st.number_input("Amount", min_value=1.0, step=1.0)
        today = date.today().isoformat()
        if st.button("Submit"):
            add_deposit(amount, selected, today)
            st.success("Deposit recorded!")
            st.experimental_rerun()
    else:
        st.warning("Please add roommates first.")

elif choice == "Remove Roommate":
    st.subheader("🔴 Remove Roommate")
    mates = get_roommates()
    if mates:
        selected = st.selectbox("Select Roommate to Remove", mates)
        if st.button("Remove"):
            remove_roommate(selected)
            st.warning(f"Roommate '{selected}' removed.")
            st.experimental_rerun()
    else:
        st.info("No roommates to remove.")
