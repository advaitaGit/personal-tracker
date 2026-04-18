import streamlit as st
import pandas as pd
from datetime import datetime
# CRITICAL: Added delete_expense to the import list below
from db_helper import get_expenses, insert_expense, delete_expense, get_balance, update_balance

def check_password():
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.warning("Please login via the Command Center (Edit page) first.")
        return False
    return True

if check_password():
    st.title("💸 Expense Tracker")

    # --- 1. ADD EXPENSE ---
    with st.form("expense_form", clear_on_submit=True):
        e_desc = st.text_input("Description")
        col1, col2 = st.columns(2)
        with col1:
            e_amount = st.number_input("Amount (RM)", min_value=0.0)
            e_type = st.selectbox("Category", ["Family Expense", "Personal", "Wife"])
        with col2:
            e_date = st.date_input("Date", datetime.today())
        
        if st.form_submit_button("Record Expense"):
            insert_expense({"date": str(e_date), "description": e_desc, "amount": e_amount, "expense_type": e_type})
            cur = get_balance()
            update_balance(cur - e_amount)
            st.success("Expense Recorded!")
            st.rerun()

    st.divider()

    # --- 2. HISTORY & DELETE ---
    st.subheader("Expense History")
    all_exp = get_expenses()
    
    if all_exp:
        df_exp = pd.DataFrame(all_exp)
        st.dataframe(df_exp[["date", "description", "expense_type", "amount"]], use_container_width=True, hide_index=True)
        
        with st.expander("🗑️ Delete an Expense"):
            # Map description to ID for deletion
            options = {f"{x['date']} | {x['description']} (RM{x['amount']})": x['id'] for x in all_exp}
            to_delete = st.selectbox("Select item to remove", options.keys())
            
            if st.button("Delete Selected Expense", type="primary"):
                expense_id = options[to_delete]
                delete_expense(expense_id) # This will now work!
                st.warning("Deleted. Note: Funds are not automatically refunded.")
                st.rerun()