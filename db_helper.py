import streamlit as st
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_balance():
    endpoint = f"{URL}/rest/v1/app_config?key=eq.grab_balance&select=value"
    res = requests.get(endpoint, headers=HEADERS, verify=False)
    data = res.json()
    return float(data[0]['value']) if data else 0.0

def update_balance(new_value):
    endpoint = f"{URL}/rest/v1/app_config?key=eq.grab_balance"
    requests.patch(endpoint, headers=HEADERS, json={"value": new_value}, verify=False)

def get_goals():
    endpoint = f"{URL}/rest/v1/goals?select=*&order=rank.asc"
    res = requests.get(endpoint, headers=HEADERS, verify=False)
    return res.json()

def upsert_goals(records):
    endpoint = f"{URL}/rest/v1/goals"
    headers = HEADERS.copy()
    headers["Prefer"] = "resolution=merge-duplicates, return=minimal"
    # Clean records to remove any NaN or Null values before sending
    cleaned = [{k: v for k, v in r.items() if v is not None and str(v) != 'nan'} for r in records]
    res = requests.post(endpoint, headers=headers, json=cleaned, verify=False)
    res.raise_for_status()

def insert_goal(goal_data):
    endpoint = f"{URL}/rest/v1/goals"
    res = requests.post(endpoint, headers=HEADERS, json=goal_data, verify=False)
    res.raise_for_status()

def get_expenses():
    endpoint = f"{URL}/rest/v1/expenses?select=*&order=date.desc"
    res = requests.get(endpoint, headers=HEADERS, verify=False)
    return res.json()

def insert_expense(expense_data):
    endpoint = f"{URL}/rest/v1/expenses"
    res = requests.post(endpoint, headers=HEADERS, json=expense_data, verify=False)
    res.raise_for_status()

def delete_expense(expense_id):
    endpoint = f"{URL}/rest/v1/expenses?id=eq.{expense_id}"
    res = requests.delete(endpoint, headers=HEADERS, verify=False)
    res.raise_for_status()