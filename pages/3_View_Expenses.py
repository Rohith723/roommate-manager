import streamlit as st
import pandas as pd
from database import get_connection

st.title("📋 View All Expenses")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)

if df.empty:
    st.info("No expenses recorded yet.")
else:
    st.dataframe(df, use_container_width=True)
