import streamlit as st
import pandas as pd
from db_helper import get_balance, update_balance, get_goals, upsert_goals, insert_goal

def check_password():
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        pwd = st.text_input("Enter Admin Key", type="password")
        if st.button("Login"):
            if pwd == st.secrets["password"]:
                st.session_state["authenticated"] = True
                st.rerun()
        return False
    return True

if check_password():
    st.title("⚙️ Command Center")
    
    # --- 1. FORM FOR NEW GOALS ---
    with st.expander("➕ Add New Debt/Goal", expanded=False):
        with st.form("new_goal_form", clear_on_submit=True):
            name = st.text_input("Name")
            amount = st.number_input("Amount (RM)", min_value=0.0)
            rank = st.number_input("Rank", min_value=1, step=1)
            deadline = st.date_input("Deadline")
            priority = st.selectbox("Priority", ["Normal", "High"])
            if st.form_submit_button("Create Goal"):
                # This is where the insert_goal function is called
                insert_goal({"name": name, "amount": amount, "rank": rank, "deadline": str(deadline), "priority": priority})
                st.success("Goal Created!")
                st.rerun()

    st.divider()
    
    # --- 2. BALANCE UPDATE ---
    cur = get_balance()
    st.subheader(f"Current Balance: RM {cur}")
    inc = st.number_input("Add Funds (RM)", min_value=0.0)
    if st.button("Update Balance"):
        update_balance(cur + inc)
        st.rerun()

    st.divider()

    # --- 3. TABLE EDITOR ---
    st.subheader("Edit Existing Goals")
    data = get_goals()
    if data:
        df = pd.DataFrame(data)
        edited = st.data_editor(df, use_container_width=True, hide_index=True)
        if st.button("Save Table Changes"):
            upsert_goals(edited.to_dict(orient="records"))
            st.success("Saved!")
            st.rerun()