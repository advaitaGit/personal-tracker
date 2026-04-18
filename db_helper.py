import streamlit as st
import requests
import urllib3

# Suppress DXC Proxy warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- BALANCE ---
def get_balance():
    res = requests.get(f"{URL}/rest/v1/app_config?key=eq.grab_balance&select=value", headers=HEADERS, verify=False)
    return float(res.json()[0]['value']) if res.json() else 0.0

def update_balance(new_value):
    requests.patch(f"{URL}/rest/v1/app_config?key=eq.grab_balance", headers=HEADERS, json={"value": new_value}, verify=False)

# --- GOALS ---
def get_goals():
    res = requests.get(f"{URL}/rest/v1/goals?select=*&order=rank.asc", headers=HEADERS, verify=False)
    return res.json()

def insert_goal(goal_data):
    requests.post(f"{URL}/rest/v1/goals", headers=HEADERS, json=goal_data, verify=False).raise_for_status()

def upsert_goals(records):
    cleaned = [{k: v for k, v in r.items() if v is not None and str(v) != 'nan'} for r in records]
    headers = HEADERS.copy()
    headers["Prefer"] = "resolution=merge-duplicates, return=minimal"
    requests.post(f"{URL}/rest/v1/goals", headers=headers, json=cleaned, verify=False).raise_for_status()

# --- EXPENSES ---
def get_expenses():
    res = requests.get(f"{URL}/rest/v1/expenses?select=*&order=date.desc", headers=HEADERS, verify=False)
    return res.json()

def insert_expense(expense_data):
    requests.post(f"{URL}/rest/v1/expenses", headers=HEADERS, json=expense_data, verify=False).raise_for_status()

def delete_expense(expense_id):
    requests.delete(f"{URL}/rest/v1/expenses?id=eq.{expense_id}", headers=HEADERS, verify=False).raise_for_status()