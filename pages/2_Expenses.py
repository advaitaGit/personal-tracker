import streamlit as st
import pandas as pd
from datetime import datetime
# Change the import line to this:
from db_helper import get_balance, update_balance, get_expenses, insert_expense

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

    all_expenses = get_expenses()
    total_expenses = sum(item.get("amount", 0) for item in all_expenses)
    
    st.metric("Total Expenses Logged", f"RM {total_expenses:.2f}")
    st.divider()

    # --- ADD EXPENSE FORM ---
    st.subheader("Log a New Expense")
    with st.form("expense_form"):
        e_desc = st.text_input("What was it for?")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            e_amount = st.number_input("Amount (RM)", min_value=0.1, step=10.0)
        with col2:
            e_type = st.selectbox("Category", ["Family Expense", "Personal", "Wife"])
        with col3:
            e_date = st.date_input("Date", datetime.today())
        
        submitted = st.form_submit_button("Record Expense")
        if submitted:
            # Use our new REST function instead of the SDK
            insert_expense({
                "date": str(e_date),
                "description": e_desc,
                "amount": float(e_amount),
                "expense_type": e_type
            })
            
            # Deduct from Grab balance
            current_bal = get_balance()
            update_balance(current_bal - float(e_amount))
            
            st.success(f"Recorded RM {e_amount}. Deducted from funds.")
            st.rerun()

    st.divider()

    # --- VIEW HISTORY ---
    st.subheader("Expense History")
    
    if not all_expenses:
        st.info("No expenses recorded yet.")
    else:
        df_expenses = pd.DataFrame(all_expenses)
        
        # Add a quick filter
        filter_type = st.selectbox("Filter by Category", ["All", "Family Expense", "Personal", "Wife"])
        
        if filter_type != "All":
            df_expenses = df_expenses[df_expenses['expense_type'] == filter_type]
            
        st.dataframe(
            df_expenses[["date", "description", "expense_type", "amount"]], 
            use_container_width=True,
            hide_index=True
        )