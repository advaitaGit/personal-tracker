import streamlit as st
import pandas as pd
import json
import os

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
    data = load_data()

    # --- FUNDS UPDATE ---
    st.subheader("Update Funds Collected")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_earnings = st.number_input("Add new income (RM)", min_value=0.0, step=10.0)
        if st.button("Add to Balance"):
            data["grab_balance"] += new_earnings
            save_data(data)
            st.success(f"Added RM {new_earnings}. New Balance: RM {data['grab_balance']:.2f}")
            st.rerun()
            
    with col2:
        st.write("") # Spacing
        st.write("") 
        if st.button("🚨 Reset Funds to 0", type="primary"):
            data["grab_balance"] = 0.0
            save_data(data)
            st.success("Funds reset!")
            st.rerun()

    st.divider()

    # --- EDIT, DELETE, REORDER DEBTS ---
    st.subheader("Manage Targets & Debts")
    st.caption("Check the 'Paid' box to move the waterfall to the next item.")
    
    if not data["goals"]:
        df = pd.DataFrame(columns=["rank", "name", "amount", "deadline", "priority", "paid"])
    else:
        df = pd.DataFrame(data["goals"])
        if "paid" not in df.columns:
            df["paid"] = False # Add the paid column if it doesn't exist yet

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "rank": st.column_config.NumberColumn("Rank", min_value=1, step=1),
            "amount": st.column_config.NumberColumn("Amount (RM)", min_value=0.0, format="%.2f"),
            "priority": st.column_config.SelectboxColumn("Priority", options=["Normal", "High"]),
            "paid": st.column_config.CheckboxColumn("Paid? ✅")
        }
    )

    if st.button("Save Debt Changes"):
        data["goals"] = edited_df.to_dict(orient="records")
        save_data(data)
        st.success("Targets updated successfully!")