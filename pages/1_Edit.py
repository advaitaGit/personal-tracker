import streamlit as st
import pandas as pd
# Change the import line to this:
from db_helper import get_balance, update_balance, get_goals, upsert_goals

def check_password():
    admin_pass = st.secrets.get("password", "admin123") 
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        pwd = st.text_input("Enter Admin Key", type="password")
        if st.button("Login"):
            if pwd == admin_pass:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect Password")
        return False
    return True

if check_password():
    st.title("⚙️ Command Center")
    
    # --- FUNDS UPDATE ---
    st.subheader("Update Funds Collected")
    current_bal = get_balance()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_earnings = st.number_input("Add new income (RM)", min_value=0.0, step=10.0)
        if st.button("Add to Balance"):
            update_balance(current_bal + new_earnings)
            st.success(f"Added RM {new_earnings}. New Balance: RM {current_bal + new_earnings:.2f}")
            st.rerun()
            
    with col2:
        st.write("") 
        st.write("") 
        if st.button("🚨 Reset Funds to 0", type="primary"):
            update_balance(0.0)
            st.success("Funds reset!")
            st.rerun()

    st.divider()

    # --- EDIT DEBTS ---
    st.subheader("Manage Targets & Debts")
    st.caption("Check the 'Paid' box to skip the item. Edit details directly in the table.")
    
    goals_data = get_goals()
    if not goals_data:
        df = pd.DataFrame(columns=["id", "rank", "name", "amount", "deadline", "priority", "paid"])
    else:
        df = pd.DataFrame(goals_data)

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": None, # Hide the database ID from the UI
            "rank": st.column_config.NumberColumn("Rank", min_value=1, step=1),
            "amount": st.column_config.NumberColumn("Amount (RM)", min_value=0.0, format="%.2f"),
            "priority": st.column_config.SelectboxColumn("Priority", options=["Normal", "High"]),
            "paid": st.column_config.CheckboxColumn("Paid? ✅")
        }
    )

    if st.button("Save Debt Changes"):
        records = edited_df.to_dict(orient="records")
        # Use our new REST function instead of the SDK
        upsert_goals(records)
        st.success("Targets updated in Database!")
        st.rerun()