import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

st.title("📊 Dashboard")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM expenses", conn)

if df.empty:
    st.info("No data to display.")
else:
    total_spent = df['amount'].sum()
    st.metric("Total Spent", f"₹{total_spent:.2f}")

    st.subheader("Spending by Category")
    fig = px.pie(df, names='category', values='amount', title='Expenses Breakdown')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Amount Paid by Each Roommate")
    by_roommate = df.groupby("paid_by")["amount"].sum().reset_index()
    fig2 = px.bar(by_roommate, x="paid_by", y="amount", title="Total Paid", text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)
