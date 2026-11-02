import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1IpB41qL59I3YaW_XE_-G58I63ux0sxLZEx-AMSGbFf4"

# Logo
for f in ["agaram_logo.jpg","logo.png","AGARAM LOGO.jpg","agaram_logo.png"]:
    if os.path.exists(f):
        st.image(f, width='stretch')
        break

try:
    conn = st.connection("gsheets", type="GSheetsConnection")
    USE_SHEET = True
except:
    USE_SHEET = False
    conn = None

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
    return True

menu = st.sidebar.selectbox("Menu", ["Home","Add Staff","Add Working Side Name","Daily Attendance","Salary Report","View Staff List"])

if menu == "Home":
    st.header("🏗️ AGARAM Dashboard")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Staff", len(load_data("staff")))
    c2.metric("Sites", len(load_data("sites")))
    c3.metric("Attendance Records", len(load_data("attendance")))
    if not USE_SHEET:
        st.warning("Running Local Mode - Add Secrets to make permanent")

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
                st.success(f"✅ {name} Saved!")
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
        
        attend_df = load_data("attendance")
        st.write("---")
        for idx, row in staff_df.iterrows():
            with st.container(border=True):
                col1,col2,col3,col4 = st.columns([2,1,1,1])
                col1.write(f"**{row['Name']}** ({row.get('Job Role','')})")
                status = col2.selectbox("Status", ["Present","Absent","Half Day"], key=f"st_{idx}_{row['Name']}")
                adv = col3.number_input("Advance ₹", min_value=0, value=0, key=f"ad_{idx}_{row['Name']}")
                if col4.button("Save", key=f"bt_{idx}_{row['Name']}"):
                    daily = float(row['Daily Salary']) if pd.notna(row['Daily Salary']) else 0
                    if status=="Present":
                        sal = daily - adv
                    elif status=="Half Day":
                        sal = (daily/2) - adv
                    else:
                        sal = -adv
                    new_entry = {"Date":str(sel_date),"Staff ID":row['Staff ID'],"Name":row['Name'],"Site Name":sel_site,"Status":status,"Advance":adv,"Salary":sal}
                    attend_df = pd.concat([attend_df, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(attend_df, "attendance")
                    st.toast(f"{row['Name']} - {status} Saved!")
        st.write("---")
        st.subheader("Today's Records")
        st.dataframe(load_data("attendance"), width='stretch')

elif menu == "Salary Report":
    st.header("Salary Report")
    adf = load_data("attendance")
    if len(adf)==0:
        st.info("No attendance yet")
    else:
        # Filter by date/site
        f1,f2 = st.columns(2)
        date_filter = f1.text_input("Filter by Date (YYYY-MM-DD) - leave empty for all")
        site_filter = f2.text_input("Filter by Site")
        if date_filter:
            adf = adf[adf['Date'].astype(str).str.contains(date_filter)]
        if site_filter:
            adf = adf[adf['Site Name'].astype(str).str.contains(site_filter)]
        
        st.dataframe(adf, width='stretch')
        # Summary
        if "Salary" in adf.columns:
            total_sal = pd.to_numeric(adf["Salary"], errors='coerce').sum()
            total_adv = pd.to_numeric(adf["Advance"], errors='coerce').sum()
            c1,c2 = st.columns(2)
            c1.metric("Total Salary to Pay", f"₹ {total_sal}")
            c2.metric("Total Advance", f"₹ {total_adv}")
        st.download_button("📥 Download Excel", adf.to_csv(index=False), "salary_report.csv")

elif menu == "View Staff List":
    st.header("All Staff")
    st.dataframe(load_data("staff"), width='stretch')
