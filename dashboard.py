
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_NAME = Path(__file__).resolve().parent / "expense_tracker.db"

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
)

st.title("💰 Personal Expense Tracker")
st.caption("Your personal income and expense dashboard")


@st.cache_data
def load_transactions():
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(
            """
            SELECT id, transaction_date, type, category, amount
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
            """,
            conn,
        )

    return df


df = load_transactions()

if df.empty:
    st.info("No transactions yet. Add income or expenses using your console tracker.")
    st.stop()

df["amount"] = pd.to_numeric(df["amount"])
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

income = df.loc[df["type"] == "income", "amount"].sum()
expenses = df.loc[df["type"] == "expense", "amount"].sum()
balance = income - expenses

col1, col2, col3 = st.columns(3)

col1.metric("Total Income", f"{income:,.2f}")
col2.metric("Total Expenses", f"{expenses:,.2f}")
col3.metric("Current Balance", f"{balance:,.2f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Expenses by Category")
    expense_df = df[df["type"] == "expense"]

    if expense_df.empty:
        st.info("No expenses to chart yet.")
    else:
        category_totals = expense_df.groupby("category")["amount"].sum()
        st.bar_chart(category_totals)

with right:
    st.subheader("Income vs Expenses")
    comparison = pd.Series(
        {"Income": income, "Expenses": expenses}
    )
    st.bar_chart(comparison)

st.subheader("Transaction History")

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_type = st.selectbox(
        "Filter by type",
        ["All", "income", "expense"],
    )

with filter_col2:
    categories = ["All"] + sorted(df["category"].unique().tolist())
    selected_category = st.selectbox("Filter by category", categories)

filtered_df = df.copy()

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["type"] == selected_type]

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["category"] == selected_category
        ]

display_df = filtered_df.rename(
    columns={
        "id": "ID",
        "transaction_date": "Date",
        "type": "Type",
        "category": "Category",
        "amount": "Amount",
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)
