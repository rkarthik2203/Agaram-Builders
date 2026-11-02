import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")

# --- LOGO HEADER ---
try:
    st.image("agaram_logo.jpg", use_container_width=True)
except:
    st.title("🏗️ AGARAM BUILDERS & CONSTRUCTION")
    st.markdown("#### நம்பிக்கை. தரம். நேர்மை. | SAFE WORK STRONG FUTURE")

st.markdown("---")

# --- DATA FILES ---
STAFF_FILE = "agaram_staff.csv"
ATTEND_FILE = "agaram_attendance.csv"
SITE_FILE = "agaram_sites.csv"

if not os.path.exists(STAFF_FILE):
    pd.DataFrame(columns=["Staff ID","Name","Phone","Job Role","Daily Salary","Working Side Name"]).to_csv(STAFF_FILE, index=False)
if not os.path.exists(SITE_FILE):
    pd.DataFrame(columns=["Site Name","Location","Supervisor"]).to_csv(SITE_FILE, index=False)
if not os.path.exists(ATTEND_FILE):
    pd.DataFrame(columns=["Date","Staff ID","Name","Site Name","Status","Advance","Salary"]).to_csv(ATTEND_FILE, index=False)

menu = st.sidebar.selectbox("Menu", ["🏠 Home","👷 Add Staff","🏗️ Add Working Side Name","📝 Daily Attendance","💰 Salary Report","📋 View Staff List"])
st.sidebar.markdown("### AGARAM BUILDERS")
st.sidebar.info("நம்பிக்கை. தரம். நேர்மை.\n\nSAFE WORK STRONG FUTURE")

if menu == "🏠 Home":
    st.success("### Welcome to AGARAM Builders Management System")
    col1,col2,col3 = st.columns(3)
    staff_df = pd.read_csv(STAFF_FILE)
    site_df = pd.read_csv(SITE_FILE)
    attend_df = pd.read_csv(ATTEND_FILE)
    col1.metric("Total Staff", len(staff_df))
    col2.metric("Working Sites", len(site_df))
    col3.metric("Today Entries", len(attend_df[attend_df['Date']==str(date.today())]))
    st.markdown("#### Vazhga Vaiyagam Vazhga Valamudan 🙏")

elif menu == "👷 Add Staff":
    st.header("Add New Staff")
    with st.form("staff_form"):
        sid = st.text_input("Staff ID")
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        role = st.selectbox("Job Role", ["Mason","Helper","Carpenter","Bar Bender","Supervisor","Driver","Other"])
        salary = st.number_input("Daily Salary (Rs)", min_value=0)
        site = st.text_input("Working Side Name (Default Site)")
        submit = st.form_submit_button("Save Staff")
        if submit:
            df = pd.read_csv(STAFF_FILE)
            new_row = {"Staff ID":sid,"Name":name,"Phone":phone,"Job Role":role,"Daily Salary":salary,"Working Side Name":site}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(STAFF_FILE, index=False)
            st.success(f"Staff {name} Saved!")

elif menu == "🏗️ Add Working Side Name":
    st.header("Add Working Side / Site Name")
    with st.form("site_form"):
        sname = st.text_input("Working Side Name *")
        loc = st.text_input("Location / Address")
        sup = st.text_input("Supervisor Name")
        submit = st.form_submit_button("Save Site")
        if submit:
            df = pd.read_csv(SITE_FILE)
            df = pd.concat([df, pd.DataFrame([{"Site Name":sname,"Location":loc,"Supervisor":sup}])], ignore_index=True)
            df.to_csv(SITE_FILE, index=False)
            st.success(f"Site {sname} Saved!")
    st.dataframe(pd.read_csv(SITE_FILE), use_container_width=True)

elif menu == "📝 Daily Attendance":
    st.header("Daily Attendance & Salary Entry")
    staff_df = pd.read_csv(STAFF_FILE)
    site_df = pd.read_csv(SITE_FILE)
    if len(staff_df)==0:
        st.warning("First Add Staff!")
    else:
        c1,c2 = st.columns(2)
        sel_date = c1.date_input("Date", date.today())
        site_list = site_df["Site Name"].tolist() if len(site_df)>0 else staff_df["Working Side Name"].unique().tolist()
        sel_site = c2.selectbox("Select Working Side Name", site_list)
        for idx, row in staff_df.iterrows():
            col1,col2,col3,col4 = st.columns([2,1,1,1])
            col1.write(f"{row['Name']} ({row['Staff ID']})")
            status = col2.selectbox(f"Status {idx}", ["Present","Absent","Half Day"], key=f"s{idx}")
            adv = col3.number_input(f"Advance {idx}", min_value=0, key=f"a{idx}")
            if col4.button(f"Save {idx}", key=f"b{idx}"):
                salary_calc = 0
                if status=="Present": salary_calc = row['Daily Salary'] - adv
                elif status=="Half Day": salary_calc = (row['Daily Salary']/2) - adv
                else: salary_calc = -adv
                adf = pd.read_csv(ATTEND_FILE)
                new_entry = {"Date":str(sel_date),"Staff ID":row['Staff ID'],"Name":row['Name'],"Site Name":sel_site,"Status":status,"Advance":adv,"Salary":salary_calc}
                adf = pd.concat([adf, pd.DataFrame([new_entry])], ignore_index=True)
                adf.to_csv(ATTEND_FILE, index=False)
                st.toast(f"Saved {row['Name']}")

elif menu == "💰 Salary Report":
    st.header("Salary Report")
    adf = pd.read_csv(ATTEND_FILE)
    if len(adf)==0:
        st.info("No attendance yet")
    else:
        d1,d2 = st.columns(2)
        fdate = d1.date_input("From Date", date.today())
        tdate = d2.date_input("To Date", date.today())
        filtered = adf[(adf['Date']>=str(fdate)) & (adf['Date']<=str(tdate))]
        st.dataframe(filtered, use_container_width=True)
        st.metric("Total Salary to Pay", f"Rs {filtered['Salary'].sum()}")
        st.download_button("Download Excel", filtered.to_csv(index=False), "agaram_salary.csv")

elif menu == "📋 View Staff List":
    st.header("All Staff - With Working Side Name")
    st.dataframe(pd.read_csv(STAFF_FILE), use_container_width=True)