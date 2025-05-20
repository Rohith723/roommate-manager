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
            roommate TEXT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

# ========== DB Operations ==========

def get_roommates():
    conn = get_connection()
    rows = conn.execute("SELECT name FROM roommates").fetchall()
    conn.close()
    return [r[0] for r in rows]

def add_roommate(name):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO roommates (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning(f"Roommate '{name}' already exists.")
    finally:
        conn.close()

def remove_roommate(name):
    conn = get_connection()
    conn.execute("DELETE FROM roommates WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def add_expense(roommate, amount, date, desc):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (roommate, amount, date, description) VALUES (?, ?, ?, ?)",
        (roommate, amount, date, desc)
    )
    conn.commit()
    conn.close()

def get_todays_expenses():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    rows = conn.execute(
        "SELECT roommate, amount, description FROM expenses WHERE date = ?", (today,)
    ).fetchall()
    conn.close()
    return rows

def get_todays_total_expense():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE date = ?", (today,)
    ).fetchone()[0]
    conn.close()
    return total or 0.0

def add_deposit(roommate, amount, date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO deposits (roommate, amount, date) VALUES (?, ?, ?)",
        (roommate, amount, date)
    )
    conn.commit()
    conn.close()

def get_monthly_deposits():
    today = date.today()
    first = today.replace(day=1).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    conn = get_connection()
    total = conn.execute(
        "SELECT SUM(amount) FROM deposits WHERE date BETWEEN ? AND ?", (first, today_str)
    ).fetchone()[0]
    conn.close()
    return total or 0.0

def get_deposits():
    conn = get_connection()
    rows = conn.execute("SELECT roommate, amount, date FROM deposits ORDER BY date DESC").fetchall()
    conn.close()
    return rows

# rerun helper
def rerun():
    import streamlit.runtime.scriptrunner as rs
    raise rs.RerunException(rs.RerunData())

# ========== Streamlit app ==========

st.title("🏠 Roommate Expense Manager")

menu = ["Dashboard", "Manage Roommates", "Add Expense", "Manage Deposits"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.subheader("📊 Overview (Today's Summary)")
    exp_today = get_todays_total_expense()
    dep_month = get_monthly_deposits()
    rem = dep_month - exp_today

    c1, c2, c3 = st.columns(3)
    c1.metric("💸 Today's Expenses", f"₹{exp_today:.2f}")
    c2.metric("💰 Deposits (1st–Today)", f"₹{dep_month:.2f}")
    c3.metric("🧾 Remaining Balance", f"₹{rem:.2f}")

    st.markdown("---")
    st.subheader("Roommates")
    rms = get_roommates()
    st.write(" • ".join(rms) if rms else "No roommates yet.")

    st.markdown("---")
    st.subheader("Today's Expenses Detail")
    details = get_todays_expenses()
    if details:
        for rm, amt, desc in details:
            st.write(f"- {rm} paid ₹{amt:.2f} for {desc}")
    else:
        st.info("No expenses recorded today.")

elif choice == "Manage Roommates":
    st.subheader("Manage Roommates")
    rms = get_roommates()

    col1, col2 = st.columns([2,2])
    with col1:
        name = st.text_input("Enter Name")
        if name and name not in rms and st.button("Add Roommate"):
            add_roommate(name)
            st.success(f"Added '{name}'")
            rerun()
    with col2:
        if rms:
            to_remove = st.selectbox("Select to Remove", rms)
            if st.button("Remove Roommate"):
                remove_roommate(to_remove)
                st.warning(f"Removed '{to_remove}'")
                rerun()
        else:
            st.info("No roommates to remove.")

elif choice == "Add Expense":
    st.subheader("Add Expense")
    rms = get_roommates()
    if not rms:
        st.warning("Add roommates first.")
    else:
        rm = st.selectbox("Roommate", rms)
        amt = st.number_input("Amount", min_value=0.01, format="%.2f")
        d = st.date_input("Date", value=datetime.now())
        desc = st.text_input("Description")
        if st.button("Add Expense"):
            add_expense(rm, amt, d.strftime("%Y-%m-%d"), desc)
            st.success("Expense added.")
            rerun()

elif choice == "Manage Deposits":
    st.subheader("Manage Deposits")
    rms = get_roommates()

    col1, col2 = st.columns([2,3])
    with col1:
        if not rms:
            st.warning("Add roommates first.")
        else:
            rm = st.selectbox("Roommate", rms, key="dep_rm")
            amt = st.number_input("Amount", min_value=0.01, format="%.2f", key="dep_amt")
            d = st.date_input("Date", value=datetime.now(), key="dep_date")
            if st.button("Add Deposit"):
                add_deposit(rm, amt, d.strftime("%Y-%m-%d"))
                st.success("Deposit added.")
                rerun()

    with col2:
        st.markdown("**All Deposits**")
        deps = get_deposits()
        if deps:
            for rm, amt, dt in deps:
                st.write(f"- {rm} deposited ₹{amt:.2f} on {dt}")
        else:
            st.info("No deposits yet.")
