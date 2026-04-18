import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

DATA_FILE = "goals.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if "expenses" not in data: data["expenses"] = []
            return data
    return {"grab_balance": 0.0, "goals": [], "expenses": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_password():
    admin_pass = st.secrets.get("password", "admin123") 
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.warning("Please login via the Command Center first.")
        return False
    return True

if check_password():
    st.title("💸 Expense Tracker")
    data = load_data()

    # Quick Summary
    total_expenses = sum(item.get("amount", 0) for item in data.get("expenses", []))
    st.metric("Total Expenses Logged", f"RM {total_expenses:.2f}")
    
    st.divider()

    # Add new Expense Form
    st.subheader("Log a New Expense")
    with st.form("expense_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            e_desc = st.text_input("What was it for?")
        with col2:
            e_amount = st.number_input("Amount (RM)", min_value=0.1, step=10.0)
            
        e_date = st.date_input("Date", datetime.today())
        
        submitted = st.form_submit_button("Record Expense")
        if submitted:
            data["expenses"].append({
                "date": str(e_date),
                "description": e_desc,
                "amount": float(e_amount)
            })
            # Automatically deduct from Funds Collected
            data["grab_balance"] -= float(e_amount)
            save_data(data)
            st.success(f"Recorded RM {e_amount} for {e_desc}. Deducted from total funds.")
            st.rerun()

    st.divider()

    # View & Edit History
    st.subheader("Expense History")
    if not data["expenses"]:
        st.info("No expenses recorded yet.")
    else:
        df_expenses = pd.DataFrame(data["expenses"])
        edited_expenses = st.data_editor(
            df_expenses, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "amount": st.column_config.NumberColumn("Amount (RM)", format="%.2f")
            }
        )
        
        if st.button("Save History Edits"):
            data["expenses"] = edited_expenses.to_dict(orient="records")
            save_data(data)
            st.success("Expense history updated.")