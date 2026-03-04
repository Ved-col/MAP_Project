import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from database import init_db, get_connection
from seed_data import seed_employees

st.set_page_config(layout="wide")

# Initialize DB and seed employees
init_db()
seed_employees()

conn = get_connection()

st.title("Manager Action Planning (MAP) System")

# ---------------- LOGIN ----------------
st.sidebar.header("Login")
user_id = st.sidebar.number_input("Enter Employee ID", min_value=1)

employee = pd.read_sql(f"SELECT * FROM employees WHERE employee_id={user_id}", conn)

if employee.empty:
    st.warning("Enter valid Employee ID")
    st.stop()

role = employee.iloc[0]["role"]
zone = employee.iloc[0]["zone"]
level = employee.iloc[0]["level"]

st.sidebar.write("Role:", role)

# ---------------- ELIGIBILITY ----------------
if role == "Manager" and level != "Level 2":
    st.error("You are not eligible to create Action Plans")
    st.stop()

# ================= MANAGER =================
if role == "Manager":

    st.header("Manager Dashboard")

    # -------- Create Plan --------
    framework = st.selectbox("Framework Element (1-12)", list(range(1,13)))
    title = st.text_input("Title")
    desc = st.text_area("Description")

    if st.button("Create Action Plan"):
        try:
            conn.execute("""
            INSERT INTO action_plans
            (manager_id, framework_element, title, description,
             status, created_date, last_updated)
            VALUES (?,?,?,?,?,?,?)
            """, (user_id, framework, title, desc,
                  "Initiated", datetime.now(), datetime.now()))
            conn.commit()

            # Simulated Notification
            conn.execute("""
            INSERT INTO notifications (message, created_date)
            VALUES (?, ?)
            """, (f"Action Plan created by Manager {user_id}", datetime.now()))
            conn.commit()

            st.success("Action Plan Created")

        except:
            st.error("Only one Action Plan allowed per Framework Element")

    # -------- Show Manager Plans --------
    df = pd.read_sql(f"""
    SELECT * FROM action_plans
    WHERE manager_id={user_id}
    """, conn)

    st.subheader("My Action Plans")
    st.dataframe(df)

    # -------- Update Section --------
    if not df.empty:

        plan_id = st.selectbox("Select Plan ID", df["action_plan_id"])

        # ----- Show Progress History -----
        st.subheader("Progress History")

        progress_df = pd.read_sql(f"""
        SELECT update_text, update_date
        FROM progress_updates
        WHERE action_plan_id = {plan_id}
        ORDER BY update_date DESC
        """, conn)

        if not progress_df.empty:
            st.dataframe(progress_df)
        else:
            st.info("No progress updates yet.")

        # ----- Status Update -----
        st.subheader("Change Status")

        new_status = st.selectbox(
            "Select New Status",
            ["Initiated", "Ongoing", "Closed"]
        )

        if st.button("Update Status"):
            conn.execute("""
            UPDATE action_plans
            SET status=?, last_updated=?
            WHERE action_plan_id=?
            """, (new_status, datetime.now(), plan_id))
            conn.commit()
            st.success("Status Updated")

        # ----- Add Progress -----
        st.subheader("Add Progress Update")

        update_text = st.text_area("Write Progress Update")

        if st.button("Add Progress"):
            conn.execute("""
            INSERT INTO progress_updates
            (action_plan_id, updated_by, update_text, update_date)
            VALUES (?, ?, ?, ?)
            """, (plan_id, user_id, update_text, datetime.now()))
            conn.commit()
            st.success("Progress Added")

# ================= HRBP =================
elif role == "HRBP":

    st.header("HRBP Dashboard")

    st.write(f"Your Assigned Zone: {zone}")

    df = pd.read_sql(f"""
    SELECT ap.*, e.name, e.zone, e.function
    FROM action_plans ap
    JOIN employees e
    ON ap.manager_id=e.employee_id
    WHERE e.zone='{zone}'
    """, conn)

    if not df.empty:

        # Additional Zone filter (for demo flexibility)
        zone_filter = st.selectbox("Filter by Zone", ["All"] + list(df["zone"].unique()))
        manager_filter = st.selectbox("Filter by Manager", ["All"] + list(df["name"].unique()))
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df["status"].unique()))

        if zone_filter != "All":
            df = df[df["zone"] == zone_filter]

        if manager_filter != "All":
            df = df[df["name"] == manager_filter]

        if status_filter != "All":
            df = df[df["status"] == status_filter]

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Zone Report (CSV)",
            data=csv,
            file_name="zone_report.csv",
            mime="text/csv"
        )
    else:
        st.warning("No Plans in Your Zone")
# ================= ADMIN =================
elif role == "Admin":

    st.header("Admin Dashboard")

    df = pd.read_sql("SELECT * FROM action_plans", conn)
    st.dataframe(df)

    st.subheader("Notification Log")
    notif = pd.read_sql("SELECT * FROM notifications", conn)
    st.dataframe(notif)

# ================= CEO =================
elif role == "CEO":

    st.header("Leadership Dashboard")

    df = pd.read_sql("""
    SELECT ap.*, e.zone, e.function
    FROM action_plans ap
    JOIN employees e
    ON ap.manager_id = e.employee_id
    """, conn)

    if not df.empty:

        total = len(df)
        closed = len(df[df["status"]=="Closed"])
        closure_rate = round((closed/total)*100,2)

        st.metric("Total Action Plans", total)
        st.metric("Closure Rate (%)", closure_rate)

        # Zone-wise breakdown
        st.subheader("Action Plans by Zone")
        zone_df = df.groupby("zone").size().reset_index(name="Count")
        fig_zone = px.bar(zone_df, x="zone", y="Count")
        st.plotly_chart(fig_zone)

        # Framework breakdown
        st.subheader("Action Plans by Framework Element")
        framework_df = df.groupby("framework_element").size().reset_index(name="Count")
        fig_framework = px.bar(framework_df, x="framework_element", y="Count")
        st.plotly_chart(fig_framework)

        # Status distribution
        st.subheader("Status Distribution")
        fig_status = px.pie(df, names="status")
        st.plotly_chart(fig_status)

    else:
        st.warning("No Action Plans Yet")