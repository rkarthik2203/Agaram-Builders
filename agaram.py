import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")

SHEET_ID = "1IpB41qL59I3YaW_XE-_G58I63ux0sxLZEx-AMSGbFf4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"

for f in ["agaram_logo.jpg","logo.png","AGARAM LOGO.jpg"]:
    if os.path.exists(f):
        st.image(f, width='stretch')
        break

try:
    conn = st.connection("gsheets", type="GSheetsConnection")
    USE_SHEET = True
except:
    USE_SHEET = False

def load_data(ws):
    if USE_SHEET:
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet=ws, ttl=0)
            df = df.dropna(how='all')
            if not df.empty:
                return df
        except:
            pass
    if os.path.exists(f"{ws}.csv"):
        try:
            return pd.read_csv(f"{ws}.csv")
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df, ws):
    if USE_SHEET:
        try:
            conn.update(spreadsheet=SHEET_URL, worksheet=ws, data=df)
        except Exception as e:
            st.error(f"Sheet Error: {e}")
    df.to_csv(f"{ws}.csv", index=False)

menu = st.sidebar.selectbox("Menu", ["Home","Add Staff","Add Working Side Name","Daily Attendance","Salary Report","View Staff List"])

if menu == "Home":
    st.header("🏗️ AGARAM Dashboard")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Staff", len(load_data("staff")))
    c2.metric("Sites", len(load_data("sites")))
    c3.metric("Attendance", len(load_data("attendance")))
    st.success("✅ Google Sheet Connected - Data Permanent!")

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
                df = load_data("staff")
                df = pd.concat([df, pd.DataFrame([{"Staff ID":sid,"Name":name,"Phone":phone,"Job Role":role,"Daily Salary":salary,"Working Side Name":site}])], ignore_index=True)
                save_data(df, "staff")
                st.success(f"✅ {name} Saved to Google Sheet!")
                st.balloons()
    st.dataframe(load_data("staff"), width='stretch')

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
                df = load_data("sites")
                df = pd.concat([df, pd.DataFrame([{"Site Name":sname,"Location":loc,"Supervisor":sup}])], ignore_index=True)
                save_data(df, "sites")
                st.success(f"✅ {sname} Saved!")
    st.dataframe(load_data("sites"), width='stretch')

elif menu == "Daily Attendance":
    st.header("Daily Attendance + Advance")
    staff_df = load_data("staff")
    site_df = load_data("sites")
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
                    adf = load_data("attendance")
                    new_entry = {"Date":str(sel_date),"Staff ID":row['Staff ID'],"Name":row['Name'],"Site Name":sel_site,"Status":status,"Advance":adv,"Salary":sal}
                    adf = pd.concat([adf, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(adf, "attendance")
                    st.toast(f"✅ {row['Name']} Saved!")
        st.dataframe(load_data("attendance"), width='stretch')

elif menu == "Salary Report":
    st.header("Salary Report")
    adf = load_data("attendance")
    st.dataframe(adf, width='stretch')
    if not adf.empty and "Salary" in adf.columns:
        st.metric("Total to Pay", f"₹ {pd.to_numeric(adf['Salary'], errors='coerce').sum()}")
    if not adf.empty:
        st.download_button("📥 Download Excel", adf.to_csv(index=False), "salary_report.csv")

elif menu == "View Staff List":
    st.header("All Staff")
    st.dataframe(load_data("staff"), width='stretch')
