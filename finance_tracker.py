import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

# Initialize session state for storing transactions
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []

# Database setup
def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            description TEXT,
            type TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Add a new transaction
def add_transaction(date, category, amount, description, type):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (date, category, amount, description, type)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, category, amount, description, type))
    conn.commit()
    conn.close()

# Load transactions from database
def load_transactions():
    conn = sqlite3.connect('finance.db')
    df = pd.read_sql_query('SELECT * FROM transactions', conn)
    conn.close()
    return df

# Delete a transaction by ID
def delete_transaction(transaction_id):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

# Clear all transactions
def clear_transactions():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions')
    conn.commit()
    conn.close()

# Summary of financial data
def get_summary(df):
    total_income = df[df['type'] == 'income']['amount'].sum()
    total_expenses = df[df['type'] == 'expense']['amount'].sum()
    balance = total_income - total_expenses
    return total_income, total_expenses, balance

# Visualization of expenses
def plot_expenses(df):
    if df[df['type'] == 'expense'].empty:
        st.write("No expense data to visualize")
        return
    fig, ax = plt.subplots()
    df[df['type'] == 'expense'].groupby('category')['amount'].sum().plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_ylabel('')
    st.pyplot(fig)

# Initialize database
init_db()

# Streamlit interface
st.title("Personal Finance Tracker")

# Input form for transactions
with st.sidebar:
    st.header("Add Transaction")
    date = st.date_input("Date", datetime.now())
    category = st.text_input("Category")
    amount = st.number_input("Amount", step=0.01)
    description = st.text_area("Description")
    type = st.selectbox("Type", ["income", "expense"])
    if st.button("Add"):
        add_transaction(date.strftime('%Y-%m-%d'), category, amount, description, type)
        st.success("Transaction added!")

# Load and display transactions
df = load_transactions()
if not df.empty:
    st.header("Transaction History")
    st.dataframe(df)

    # Display summary
    st.header("Summary")
    total_income, total_expenses, balance = get_summary(df)
    st.write(f"Total Income: ${total_income:.2f}")
    st.write(f"Total Expenses: ${total_expenses:.2f}")
    st.write(f"Balance: ${balance:.2f}")

    # Display visualization
    st.header("Expense Visualization")
    plot_expenses(df)

    # Delete a transaction
    st.header("Delete a Transaction")
    transaction_id = st.number_input("Enter Transaction ID to Delete", min_value=0)
    if st.button("Delete Transaction"):
        delete_transaction(transaction_id)
        st.success("Transaction deleted!")
        st.experimental_rerun()

    # Clear all transactions
    st.header("Clear All Transactions")
    if st.button("Clear All"):
        clear_transactions()
        st.success("All transactions cleared!")
        st.experimental_rerun()
else:
    st.write("No transactions found.")
