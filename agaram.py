import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1IpB41qL59I3YaW_XE_-G58I63ux0sxLZEx-AMSGbFf4"

logo_file = None
for f in ["agaram_logo.jpg", "logo.png", "AGARAM LOGO.jpg"]:
    if os.path.exists(f):
        logo_file = f
        break
if logo_file:
    st.image(logo_file, width='stretch')

# Try Google Sheet, but don't fail if not connected
try:
    conn = st.connection("gsheets", type="GSheetsConnection")
    USE_SHEET = True
except:
    USE_SHEET = False
    conn = None

def load_data(worksheet):
    if USE_SHEET:
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet=worksheet, ttl=0)
            df = df.dropna(how='all')
            if not df.empty:
                return df
        except:
            pass
    # Local fallback - this will ALWAYS work
    if os.path.exists(f"{worksheet}.csv"):
        return pd.read_csv(f"{worksheet}.csv")
    return pd.DataFrame()

def save_data(df, worksheet):
    ok = False
    if USE_SHEET:
        try:
            conn.update(spreadsheet=SHEET_URL, worksheet=worksheet, data=df)
            ok = True
        except Exception as e:
            st.error(f"Sheet Error: {e}")
    # Always save locally too
    df.to_csv(f"{worksheet}.csv", index=False)
    return True

menu = st.sidebar.selectbox("Menu", ["Home","Add Staff","Add Working Side Name","Daily Attendance","Salary Report","View Staff List"])

if menu == "Add Staff":
    st.header("Add New Staff")
    with st.form("staff_form", clear_on_submit=True):
        sid = st.text_input("Staff ID")
        name = st.text_input("Name *")
        phone = st.text_input("Phone")
        role = st.selectbox("Job Role", ["Mason","Helper","Carpenter","Bar Bender","Supervisor","Driver","Other"])
        salary = st.number_input("Daily Salary", min_value=0, value=1500)
        site = st.text_input("Working Side Name")
        submit = st.form_submit_button("💾 Save")
        if submit:
            if not name:
                st.error("Name required!")
            else:
                df = load_data("staff")
                new_row = {"Staff ID":sid,"Name":name,"Phone":phone,"Job Role":role,"Daily Salary":salary,"Working Side Name":site}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df, "staff")
                st.success(f"✅ {name} Saved! Refresh page to see in table")
                st.balloons()
    df_show = load_data("staff")
    st.write(f"Total Staff: {len(df_show)}")
    st.dataframe(df_show, width='stretch')

elif menu == "View Staff List":
    st.dataframe(load_data("staff"), width='stretch')
elif menu == "Home":
    st.metric("Total Staff", len(load_data("staff")))
else:
    st.info("Use Add Staff to add data")
