import streamlit as st
from database import get_connection

st.title("💸 Add New Expense")

conn = get_connection()
roommates = conn.execute("SELECT name FROM roommates").fetchall()
roommate_names = [r[0] for r in roommates]
conn.close()

if not roommate_names:
    st.warning("Please add at least one roommate before adding expenses.")
else:
    category = st.selectbox("Category", ["Rent", "Electricity", "Water", "Internet", "Groceries", "Others"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    paid_by = st.selectbox("Paid By", roommate_names)
    date = st.date_input("Date")
    description = st.text_area("Description (optional)")

    if st.button("Add Expense"):
        conn = get_connection()
        conn.execute(
            "INSERT INTO expenses (date, category, amount, paid_by, description) VALUES (?, ?, ?, ?, ?)",
            (str(date), category, amount, paid_by, description)
        )
        conn.commit()
        conn.close()
        st.success("Expense added successfully!")
