import streamlit as st
import pandas as pd
from db_helper import get_balance, get_goals

st.set_page_config(page_title="Alan's Tracker", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# Fetch live data from Supabase
grab_balance = get_balance()
all_goals = get_goals()

st.title("🎯 Goal & Debt Overview")
st.metric("Funds Collected", f"RM {grab_balance:.2f}")
st.divider()

if not all_goals:
    st.info("No goals added yet. Go to the Edit page.")

active_goals = [g for g in all_goals if not g.get("paid", False)]
paid_goals = [g for g in all_goals if g.get("paid", False)]

remaining_funds = grab_balance

# ACTIVE DEBTS (Waterfall Logic)
for goal in active_goals:
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            if goal["priority"] == "High":
                st.error(f"🔥 **{goal['name']}**")
            else:
                st.markdown(f"**{goal['name']}**")
            
            # Format date nicely if it exists
            due_date = goal.get('deadline')
            st.caption(f"Due: {due_date if due_date else 'No Date'}")
        with col2:
            st.metric("Target", f"RM {goal['amount']:.2f}")
        
        progress = 0.0
        if remaining_funds >= goal["amount"]:
            progress = 1.0
            remaining_funds -= goal["amount"]
        elif remaining_funds > 0:
            progress = remaining_funds / goal["amount"]
            remaining_funds = 0.0 
            
        st.progress(progress)
        
        if progress == 1.0:
            st.success("Fully Funded! Ready to Pay.")
        elif progress > 0:
            st.info("Currently allocating funds here...")

# CLEARED DEBTS
if paid_goals:
    st.write("")
    st.subheader("✅ Cleared / Paid")
    for goal in paid_goals:
        with st.container(border=True):
            st.markdown(f"~~**{goal['name']}**~~ (RM {goal['amount']:.2f})")