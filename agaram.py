import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="AGARAM Builders", page_icon="🏗️", layout="wide")

# SHEET ID - YOUR ID ADDED
SHEET_ID = "1IpB41qL59I3YaW_XE_-G58I63ux0sxLZEx-AMSGbFf4"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"

logo_file = None
for f in ["agaram_logo.jpg", "logo.png", "AGARAM LOGO.jpg"]:
    if os.path.exists(f):
        logo_file = f
        break
if logo_file:
    st.image(logo_file, use_container_width=True)
else:
    st.title("🏗️ AGARAM Builders & Consultant")

st.markdown("---")

# Connection
try:
    conn = st.connection("gsheets", type="GSheetsConnection")
    USE_SHEET = True
except Exception as e:
    USE_SHEET = False
    st.warning(f"Google Sheet connect pending: {e}")

def load_data(worksheet):
    try:
        if USE_SHEET:
            df = conn.read(spreadsheet=SHEET_URL, worksheet=worksheet, ttl=0)
            df = df.dropna(how='all')
            # Remove empty rows where first column empty
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
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

menu = st.sidebar.selectbox("Menu", ["Home","Add Staff","Add Working Side Name","Daily Attendance","Salary Report","View Staff List"])
if logo_file:
    st.sidebar.image(logo_file, use_container_width=True)
    st.sidebar.success("✅ Permanent Storage")

if menu == "Home":
    st.success("✅ Google Sheet-ல் Permanent Save! Data எப்போதும் அழியாது!")
    staff_df = load_data("staff")
    site_df = load_data("sites")
    attend_df = load_data("attendance")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Staff", len(staff_df))
    c2.metric("Working Sites", len(site_df))
    c3.metric("Today Entries", len(attend_df))
    st.info(f"Sheet Link: {SHEET_URL}")
    if len(staff_df)>0:
        st.subheader("Recent Staff")
        st.dataframe(staff_df.tail(5), use_container_width=True)

elif menu == "Add Staff":
    st.header("Add New Staff - Permanent Save")
    with st.form("staff_form"):
        sid = st.text_input("Staff ID")
        name = st.text_input("Name *")
        phone = st.text_input("Phone")
        role = st.selectbox("Job Role", ["Mason","Helper","Carpenter","Bar Bender","Supervisor","Driver","Other"])
        salary = st.number_input("Daily Salary", min_value=0, value=800)
        site = st.text_input("Working Side Name")
        submit = st.form_submit_button("💾 Permanent Save to Google Sheet")
        if submit:
            if not name:
                st.error("Name required!")
            else:
                df = load_data("staff")
                new_row = {"Staff ID":sid,"Name":name,"Phone":phone,"Job Role":role,"Daily Salary":salary,"Working Side Name":site}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                if save_data(df, "staff"):
                    st.success(f"✅ {name} Google Sheet-ல் Permanent Save! எப்போதும் அழியாது!")
                    st.balloons()
                else:
                    st.error("Save failed - Check Secrets")
    st.dataframe(load_data("staff"), use_container_width=True)

elif menu == "Add Working Side Name":
    st.header("Add Working Side Name")
    with st.form("site_form"):
        sname = st.text_input("Working Side Name *")
        loc = st.text_input("Location")
        sup = st.text_input("Supervisor")
        submit = st.form_submit_button("💾 Save Permanent")
        if submit:
            if not sname:
                st.error("Site Name required")
            else:
                df = load_data("sites")
                df = pd.concat([df, pd.DataFrame([{"Site Name":sname,"Location":loc,"Supervisor":sup}])], ignore_index=True)
                if save_data(df, "sites"):
                    st.success(f"✅ {sname} Permanent Save!")
    st.dataframe(load_data("sites"), use_container_width=True)

elif menu == "Daily Attendance":
    st.header("Daily Attendance - Permanent")
    staff_df = load_data("staff")
    site_df = load_data("sites")
    if len(staff_df)==0:
        st.warning("First Add Staff in Add Staff menu!")
    else:
        c1,c2 = st.columns(2)
        sel_date = c1.date_input("Date", date.today())
        site_list = site_df["Site Name"].tolist() if len(site_df)>0 else staff_df["Working Side Name"].unique().tolist()
        site_list = [s for s in site_list if str(s).strip() != '']
        sel_site = c2.selectbox("Select Working Side", site_list if site_list else ["General"])
        attend_df = load_data("attendance")
        st.markdown("---")
        for idx, row in staff_df.iterrows():
            if str(row['Name']).strip() == '': continue
            col1,col2,col3,col4 = st.columns([2,1,1,1])
            col1.write(f"**{row['Name']}** ({row['Staff ID']})")
            status = col2.selectbox(f"Status", ["Present","Absent","Half Day"], key=f"s{idx}")
            adv = col3.number_input(f"Advance", min_value=0, key=f"a{idx}")
            if col4.button(f"Save", key=f"b{idx}"):
                try:
                    daily_sal = float(row['Daily Salary'])
                except:
                    daily_sal = 0
                if status=="Present":
                    salary_calc = daily_sal - adv
                elif status=="Half Day":
                    salary_calc = (daily_sal/2) - adv
                else:
                    salary_calc = -adv
                new_entry = {"Date":str(sel_date),"Staff ID":row['Staff ID'],"Name":row['Name'],"Site Name":sel_site,"Status":status,"Advance":adv,"Salary":salary_calc}
                attend_df = pd.concat([attend_df, pd.DataFrame([new_entry])], ignore_index=True)
                if save_data(attend_df, "attendance"):
                    st.toast(f"✅ {row['Name']} Saved!", icon="✅")
        st.markdown("---")
        st.subheader("Today Attendance")
        st.dataframe(load_data("attendance"), use_container_width=True)

elif menu == "Salary Report":
    st.header("Salary Report")
    adf = load_data("attendance")
    if len(adf)==0:
        st.info("No attendance yet")
    else:
        d1,d2 = st.columns(2)
        fdate = d1.date_input("From Date", date.today())
        tdate = d2.date_input("To Date", date.today())
        try:
            filtered = adf[(adf['Date']>=str(fdate)) & (adf['Date']<=str(tdate))]
        except:
            filtered = adf
        st.dataframe(filtered, use_container_width=True)
        if len(filtered)>0:
            try:
                total = pd.to_numeric(filtered['Salary'], errors='coerce').sum()
                st.metric("Total Salary", f"Rs {total}")
            except:
                pass
            st.download_button("Download Excel", filtered.to_csv(index=False), "agaram_salary.csv")

elif menu == "View Staff List":
    st.header("All Staff - Permanent Storage")
    df = load_data("staff")
    st.dataframe(df, use_container_width=True)
    if len(df)>0:
        st.download_button("Download Staff List", df.to_csv(index=False), "staff_list.csv")
