import streamlit as st
import pandas as pd
from database import get_connection, init_db

# Setup
st.set_page_config(page_title="Roommate Expense Manager", layout="wide")
st.title("🏠 Badcows")

# Initialize DB
init_db()

# Layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Welcome to Your Shared Living Expense Tracker 🎉")
    st.markdown("""
        This app helps you manage your shared expenses easily:
        - ✅ Add and manage roommates
        - 💰 Track all types of expenses
        - 📊 View analytics and summaries
        - 🧾 Never miss rent or bills again!
    """)

with col2:
    st.image("https://img.freepik.com/free-vector/house-rent-concept-illustration_114360-7371.jpg", use_column_width=True)

st.markdown("---")

# Fetch roommates
conn = get_connection()
roommates = pd.read_sql_query("SELECT name, mobile FROM roommates", conn)
expenses = pd.read_sql_query("SELECT * FROM expenses", conn)
conn.close()

# Display roommate list
st.subheader("👥 Current Roommates")
if roommates.empty:
    st.info("No roommates added yet. Go to **'Add Roommate'** to begin.")
else:
    st.dataframe(roommates, use_container_width=True)

# Display quick stats
st.subheader("📈 Quick Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Total Roommates", len(roommates))
col2.metric("Total Expenses", f"₹{expenses['amount'].sum():.2f}" if not expenses.empty else "₹0.00")
col3.metric("Total Entries", len(expenses))

st.markdown("👉 Use the **sidebar** to add roommates, record expenses, and view the dashboard.")
