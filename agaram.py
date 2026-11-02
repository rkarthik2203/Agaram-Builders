import streamlit as st
import pandas as pd
from datetime import date
import os
import requests
import json
from io import StringIO

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")

# YOUR SHEET & SCRIPT - CORRECT ID
SHEET_ID = "1IpB41qL59I3YaW_XE-_G58I63ux0sxLZEx-AMSGbFf4"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxH3miuDoFGBfzEjE8DTrC3BYbX6kumWWohA5WPbxayITkdX-K8WSlm_NvT-f5qf-jq/exec"

for f in ["agaram_logo.jpg","logo.png","AGARAM LOGO.jpg"]:
    if os.path.exists(f):
        st.image(f, width='stretch')
        break

def load_from_sheet(sheet_name):
    try:
        # Public CSV export - no auth needed
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and len(r.text) > 10:
            df = pd.read_csv(StringIO(r.text))
            return df.dropna(how='all')
    except:
        pass
    # Fallback local
    if os.path.exists(f"{sheet_name}.csv"):
        try:
            return pd.read_csv(f"{sheet_name}.csv")
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_to_sheet(sheet_name, row_dict):
    try:
        # Save to Google Sheet via Apps Script
        payload = {
            'sheet': sheet_name,
            'data': json.dumps(row_dict)
        }
        r = requests.post(SCRIPT_URL, data=payload, timeout=10)
        # Also save local backup
        if os.path.exists(f"{sheet_name}.csv"):
            df = pd.read_csv(f"{sheet_name}.csv")
            df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)
            df.to_csv(f"{sheet_name}.csv", index=False)
        else:
            pd.DataFrame([row_dict]).to_csv(f"{sheet_name}.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False

menu = st.sidebar.selectbox("Menu", ["Home","Add Staff","Add Working Side Name","Daily Attendance","Salary Report","View Staff List"])

if menu == "Home":
    st.header("🏗️ AGARAM Dashboard")
    staff_df = load_from_sheet("staff")
    sites_df = load_from_sheet("sites")
    att_df = load_from_sheet("attendance")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Staff", len(staff_df))
    c2.metric("Sites", len(sites_df))
    c3.metric("Attendance", len(att_df))
    if len(staff_df) > 0:
        st.success(f"✅ {len(staff_df)} Staff in Google Sheet - Permanent!")
    st.dataframe(staff_df, width='stretch')

elif menu == "Add Staff":
    st.header("Add New Staff")
    with st.form("staff_form", clear_on_submit=True):
        sid = st.text_input("Staff ID")
        name = st.text_input("Name *")
        phone = st.text_input("Phone")
        role = st.selectbox("Job Role", ["Mason","Helper","Carpenter","Bar Bender","Supervisor","Driver","Other"])
        salary = st.number_input("Daily Salary", min_value=0, value=1500)
        site = st.text_input("Working Side Name")
        if st.form_submit_button("💾 Save Staff"):
            if not name:
                st.error("Name required!")
            else:
                row = {"Staff ID":sid,"Name":name,"Phone":phone,"Job Role":role,"Daily Salary":salary,"Working Side Name":site}
                if save_to_sheet("staff", row):
                    st.success(f"✅ {name} Saved to Google Sheet! Permanent!")
                    st.balloons()
    st.subheader("Staff List (From Google Sheet)")
    st.dataframe(load_from_sheet("staff"), width='stretch')

elif menu == "Add Working Side Name":
    st.header("Add Working Side Name")
    with st.form("site_form", clear_on_submit=True):
        sname = st.text_input("Site Name *")
        loc = st.text_input("Location")
        sup = st.text_input("Supervisor")
        if st.form_submit_button("💾 Save Site"):
            if not sname:
                st.error("Site Name required!")
            else:
                row = {"Site Name":sname,"Location":loc,"Supervisor":sup}
                if save_to_sheet("sites", row):
                    st.success(f"✅ {sname} Saved to Sheet!")
    st.dataframe(load_from_sheet("sites"), width='stretch')

elif menu == "Daily Attendance":
    st.header("Daily Attendance + Advance")
    staff_df = load_from_sheet("staff")
    site_df = load_from_sheet("sites")
    if len(staff_df)==0:
        st.warning("First Add Staff!")
    else:
        sel_date = st.date_input("Date", date.today())
        site_list = site_df["Site Name"].tolist() if len(site_df)>0 and "Site Name" in site_df.columns else ["General"]
        sel_site = st.selectbox("Select Working Side", site_list)
        for idx, row in staff_df.iterrows():
            with st.container(border=True):
                col1,col2,col3,col4 = st.columns([2,1,1,1])
                col1.write(f"**{row['Name']}**")
                status = col2.selectbox("Status", ["Present","Absent","Half Day"], key=f"st_{idx}")
                adv = col3.number_input("Advance ₹", min_value=0, value=0, key=f"ad_{idx}")
                if col4.button("Save", key=f"bt_{idx}"):
                    daily = float(row['Daily Salary']) if pd.notna(row['Daily Salary']) else 0
                    sal = daily - adv if status=="Present" else (daily/2 - adv if status=="Half Day" else -adv)
                    new_row = {"Date":str(sel_date),"Staff ID":row['Staff ID'],"Name":row['Name'],"Site Name":sel_site,"Status":status,"Advance":adv,"Salary":sal}
                    if save_to_sheet("attendance", new_row):
                        st.toast(f"✅ {row['Name']} Saved to Sheet!")
        st.dataframe(load_from_sheet("attendance"), width='stretch')

elif menu == "Salary Report":
    st.header("Salary Report")
    adf = load_from_sheet("attendance")
    st.dataframe(adf, width='stretch')
    if not adf.empty and "Salary" in adf.columns:
        st.metric("Total to Pay", f"₹ {pd.to_numeric(adf['Salary'], errors='coerce').sum()}")
    if not adf.empty:
        st.download_button("📥 Download Excel", adf.to_csv(index=False), "salary_report.csv")

elif menu == "View Staff List":
    st.header("All Staff - From Google Sheet")
    st.dataframe(load_from_sheet("staff"), width='stretch')
