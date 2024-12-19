import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="Employee Payroll Tracking", page_icon="💵")
st.title("💵 Employee Payroll Tracking")
st.write(
    """
    This app shows how you can build an internal tool in Streamlit. Here, we are 
    implementing a support ticket workflow. The user can create a ticket, edit 
    existing tickets, and view some statistics.
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Make up some fake issue descriptions.
    names=[]
    for i in range(0,20):
        names.append("Employee "+str(i))
        
    issue_descriptions = names 

    """
    [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]
    """

    # Generate the dataframe with 100 rows/tickets.
    data = {
        "ID": [f"Payroll-{i}" for i in range(1100, 1000, -1)],
        "Employee": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Unregistered", "In Progress", "Paid"], size=100),
        "Department": np.random.choice(["Production", "Assembly", "Transportation", "Marketing", "Managment"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df
    df.to_json('Data_base.json')


# Show a section to add a new ticket.
st.header("Add a employee and worked hours")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("First Name and Last Name format")
    dpto = st.selectbox("Department", ["Production", "Assembly", "Transportation", "Marketing", "Managment"])
    rates = list(range(1,101))
    rate = st.selectbox(" Hour Rate US$", rates)
    hours = st.selectbox("Worked Hours$", list(range(1,11)))


    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"Payrrol-{recent_ticket_number+1}",
                "Employee": issue,
                "Status": "Unpaid",
                "Department": dpto,
                "Hour Rate": rate,
                "Total Hours": hours,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Employee Submitted submitted! Here are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)
    

# Show section to view and edit existing tickets in a table.
st.header("Existing payrolls")
st.write(f"Number of payrolls: `{len(st.session_state.df)}`")

st.info(
    "You can edit the payrolls by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Payroll status",
            options=["Unregistered", "In Progress", "Paid"],
            required=True,
        ),
        "Department": st.column_config.SelectboxColumn(
            "Department",
            help="Department",
            options=["Production", "Assembly", "Transportation", "Marketing", "Managment"],
            required=True,
        ),
        "Hour Rate": st.column_config.SelectboxColumn(
            "Hour Rate",
            help="Hour Rate",
            options= list(range(1,101)), #["Production", "Assembly", "Transportation", "Marketing", "Managment"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# Show some metrics and charts about the ticket.
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Unregistered"])
col1.metric(label="Number of open payrolls", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Payroll status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current payroll department")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Department:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
