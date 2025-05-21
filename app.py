import streamlit as st
import sqlite3
from datetime import datetime

# ----------------------- Database Functions -----------------------

def get_connection():
    return sqlite3.connect("roommate_expenses.db")

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT UNIQUE,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS roommates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            room_id INTEGER,
            UNIQUE(name, room_id),
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roommate TEXT,
            amount REAL,
            date TEXT,
            description TEXT,
            room_id INTEGER,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            roommate TEXT,
            date TEXT,
            room_id INTEGER,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')

    conn.commit()
    conn.close()

def register_room(room_name, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO rooms (room_name, password) VALUES (?, ?)", (room_name, password))
        conn.commit()
        st.success("Room registered successfully. Please login.")
    except sqlite3.IntegrityError:
        st.warning("Room already exists.")
    finally:
        conn.close()

def login_room(room_name, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM rooms WHERE room_name = ? AND password = ?", (room_name, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_roommates(room_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM roommates WHERE room_id = ?", (room_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_roommate(name, room_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO roommates (name, room_id) VALUES (?, ?)", (name, room_id))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning("Roommate already exists.")
    finally:
        conn.close()

def remove_roommate(name, room_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM roommates WHERE name = ? AND room_id = ?", (name, room_id))
    conn.commit()
    conn.close()

def add_expense(roommate, amount, description, room_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO expenses (roommate, amount, date, description, room_id) VALUES (?, ?, ?, ?, ?)",
              (roommate, amount, datetime.today().strftime('%Y-%m-%d'), description, room_id))
    conn.commit()
    conn.close()

def get_todays_expenses(room_id):
    conn = get_connection()
    c = conn.cursor()
    today = datetime.today().strftime('%Y-%m-%d')
    c.execute("SELECT roommate, amount, description FROM expenses WHERE date = ? AND room_id = ?", (today, room_id))
    rows = c.fetchall()
    conn.close()
    return rows

def add_deposit(amount, roommate, room_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO deposits (amount, roommate, date, room_id) VALUES (?, ?, ?, ?)",
              (amount, roommate, datetime.today().strftime('%Y-%m-%d'), room_id))
    conn.commit()
    conn.close()

def get_deposits(room_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT roommate, amount, date FROM deposits WHERE room_id = ?", (room_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------------------- Main App ----------------------------

def main():
    st.set_page_config(page_title="Roommate Expense Manager")
    st.title("Roommate Expense Manager")

    create_tables()

    if 'room_id' not in st.session_state:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            st.subheader("Login to Your Room")
            room_name = st.text_input("Room Name")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                room_id = login_room(room_name, password)
                if room_id:
                    st.session_state.room_id = room_id
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid room name or password")

        with register_tab:
            st.subheader("Register a New Room")
            new_room = st.text_input("New Room Name")
            new_password = st.text_input("Set Password", type="password")
            if st.button("Register"):
                register_room(new_room, new_password)
        return

    menu = ["Manage Roommates", "Add Expense", "View Today's Expenses", "Deposit Money", "View Deposits", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)
    room_id = st.session_state.room_id

    if choice == "Manage Roommates":
        st.subheader("Add or Remove Roommates")
        roommates = get_roommates(room_id)
        st.write("Current Roommates:", roommates)

        new_roommate = st.text_input("Enter new roommate name")
        if st.button("Add Roommate"):
            add_roommate(new_roommate, room_id)
            st.success(f"Roommate '{new_roommate}' added.")
            st.rerun()

        remove_name = st.selectbox("Select roommate to remove", roommates)
        if st.button("Remove Roommate"):
            remove_roommate(remove_name, room_id)
            st.success(f"Roommate '{remove_name}' removed.")
            st.rerun()

    elif choice == "Add Expense":
        st.subheader("Add Today's Expense")
        roommates = get_roommates(room_id)
        roommate = st.selectbox("Who paid?", roommates)
        amount = st.number_input("Amount Spent", min_value=0.0, format="%.2f")
        description = st.text_input("Description")
        if st.button("Add Expense"):
            add_expense(roommate, amount, description, room_id)
            st.success("Expense added.")

    elif choice == "View Today's Expenses":
        st.subheader("Today's Expenses")
        expenses = get_todays_expenses(room_id)
        for e in expenses:
            st.write(f"{e[0]} spent Rs. {e[1]} on {e[2]}")

    elif choice == "Deposit Money":
        st.subheader("Add Deposit")
        roommates = get_roommates(room_id)
        roommate = st.selectbox("Who deposited?", roommates)
        amount = st.number_input("Deposit Amount", min_value=0.0, format="%.2f")
        if st.button("Add Deposit"):
            add_deposit(amount, roommate, room_id)
            st.success("Deposit recorded.")

    elif choice == "View Deposits":
        st.subheader("All Deposits")
        deposits = get_deposits(room_id)
        for d in deposits:
            st.write(f"{d[0]} deposited Rs. {d[1]} on {d[2]}")

    elif choice == "Logout":
        del st.session_state.room_id
        st.success("Logged out successfully.")
        st.rerun()

if __name__ == '__main__':
    main()
