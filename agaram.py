import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")

SHEET_ID = "1IpB41qL59I3YaW_XE_-G58I63ux0sxLZEx-AMSGbFf4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"

logo_file = None
for f in ["agaram_logo.jpg", "logo.png", "AGARAM LOGO.jpg"]:
    if os.path.exists(f):
        logo_file = f
        break

if logo_file:
    st.image(logo_file, width='stretch')
else:
    st.title("🏗️ AGARAM Builders & Consultant")

# Silent connection - No yellow/green box
try:
    conn = st.connection("gsheets", type="GSheetsConnection")
    USE_SHEET = True
except:
    USE_SHEET = False

def load_data(worksheet):
    try:
        if USE_SHEET:
            df = conn.read(spreadsheet=SHEET_URL, worksheet=worksheet, ttl=0)
            df = df.dropna(how='all')
            if not df.empty:
                df = df[df.iloc[:,0].astype(str).str.strip() != '']
            return df
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

def save_data(df, worksheet):
    try:
        if USE_SHEET:
            conn.update(spreadsheet=SHEET_URL, worksheet=worksheet, data=df)
            return True
        return False
    except:
        return False

menu = st.sidebar.selectbox("Menu", ["Home","Add Staff","Add Working Side Name","Daily Attendance","Salary Report","View Staff List"])
if logo_file:
    st.sidebar.image(logo_file, width='stretch')

if menu == "Home":
    staff_df = load_data("staff")
    site_df = load_data("sites")
    attend_df = load_data("attendance")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Staff", len(staff_df))
    c2.metric("Working Sites", len(site_df))
    c3.metric("Today Entries", len(attend_df))
    if len(staff_df)>0:
        st.subheader("Recent Staff")
        st.dataframe(staff_df.tail(5), width='stretch')

elif menu == "Add Staff":
    st.header("Add New Staff")
    with st.form("staff_form"):
        sid = st.text_input("Staff ID")
        name = st.text_input("Name *")
        phone = st.text_input("Phone")
        role = st.selectbox("Job Role", ["Mason","Helper","Carpenter","Bar Bender","Supervisor","Driver","Other"])
        salary = st.number_input("Daily Salary", min_value=0, value=800)
        site = st.text_input("Working Side Name")
        submit = st.form_submit_button("💾 Save")
        if submit:
            if not name:
                st.error("Name required!")
            else:
                df = load_data("staff")
                new_row = {"Staff ID":sid,"Name":name,"Phone":phone,"Job Role":role,"Daily Salary":salary,"Working Side Name":site}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                if save_data(df, "staff"):
                    st.success(f"✅ {name} Saved!")
    st.dataframe(load_data("staff"), width='stretch')

elif menu == "Add Working Side Name":
    st.header("Add Working Side Name")
    with st.form("site_form"):
        sname = st.text_input("Working Side Name *")
        loc = st.text_input("Location")
        sup = st.text_input("Supervisor")
        submit = st.form_submit_button("💾 Save")
        if submit:
            df = load_data("sites")
            df = pd.concat([df, pd.DataFrame([{"Site Name":sname,"Location":loc,"Supervisor":sup}])], ignore_index=True)
            if save_data(df, "sites"):
                st.success(f"✅ {sname} Saved!")
    st.dataframe(load_data("sites"), width='stretch')

elif menu == "Daily Attendance":
    st.header("Daily Attendance")
    staff_df = load_data("staff")
    site_df = load_data("sites")
    if len(staff_df)==0:
        st.warning("First Add Staff!")
    else:
        c1,c2 = st.columns(2)
        sel_date = c1.date_input("Date", date.today())
        site_list = site_df["Site Name"].tolist() if len(site_df)>0 else []
        sel_site = c2.selectbox("Select Working Side", site_list if site_list else ["General"])
        attend_df = load_data("attendance")
        for idx, row in staff_df.iterrows():
            if str(row['Name']).strip() == '': continue
            col1,col2,col3,col4 = st.columns([2,1,1,1])
            col1.write(f"**{row['Name']}**")
            status = col2.selectbox("Status", ["Present","Absent","Half Day"], key=f"s{idx}")
            adv = col3.number_input("Advance", min_value=0, key=f"a{idx}")
            if col4.button("Save", key=f"b{idx}"):
                try:
                    daily_sal = float(row['Daily Salary'])
                except:
                    daily_sal = 0
                salary_calc = daily_sal - adv if status=="Present" else (daily_sal/2 - adv if status=="Half Day" else -adv)
                new_entry = {"Date":str(sel_date),"Staff ID":row['Staff ID'],"Name":row['Name'],"Site Name":sel_site,"Status":status,"Advance":adv,"Salary":salary_calc}
                attend_df = pd.concat([attend_df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(attend_df, "attendance")
        st.dataframe(load_data("attendance"), width='stretch')

elif menu == "Salary Report":
    st.header("Salary Report")
    adf = load_data("attendance")
    st.dataframe(adf, width='stretch')
    if len(adf)>0:
        st.download_button("Download Excel", adf.to_csv(index=False), "agaram_salary.csv")

elif menu == "View Staff List":
    st.header("All Staff")
    st.dataframe(load_data("staff"), width='stretch')
