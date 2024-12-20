import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


# Show app title and description
st.set_page_config(page_title="Employee Payroll Tracking", page_icon="💵")
st.title("💵 Employee Payroll Tracking")
st.write(
    """
    This app shows how you can build an internal tool in Streamlit. Here, we are 
    implementing a employee payroll workflow. The user can create a ticket, edit 
    existing tickets, and view some statistics.
    """
)

# Define a simple username-password dictionary
USER_CREDENTIALS = {
    "admin": "admin",
    "user": "user123",
}

# Authentication function
def authenticate(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        return True
    return False

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# Login logic
if not st.session_state["logged_in"]:
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")    

    if login_button:
        if authenticate(username, password):
            
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.session_state["username"] = None
                st.rerun()
                
            st.success(f"Welcome, {username}!")
            # Your app's main content goes here
            st.write("This is the main app content.")

            # Load the existing DataFrame from the JSON file

            df = pd.read_json('Data_base.json')
            st.session_state.df = df

            # Create a random Pandas DataFrame with existing tickets
            if "df" not in st.session_state:
                # Set seed for reproducibility
                np.random.seed(42)

                # Make up some fake issue descriptions
                names = [f"Employee {i}" for i in range(20)]
                issue_descriptions = names

                # Generate the DataFrame with 5 rows/tickets
                data = {
                    "ID": [f"Payroll-{i}" for i in range(1100, 1095, -1)],
                    "Employee": np.random.choice(issue_descriptions, size=5),
                    "Status": np.random.choice(["Unregistered", "In Progress", "Paid"], size=5),
                    "Department": np.random.choice(["Production", "Assembly", "Transportation", "Marketing", "Managment"], size=5),
                    "Hour Rate": np.random.choice(["1", "2", "3"], size=5),
                    "Total Hours": np.random.choice(["100", "100", "100"], size=5),
                    "Date Submitted": [
                        datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
                        for _ in range(5)
                    ],
                }
                df = pd.DataFrame(data)
                # Save the DataFrame in session state (a dictionary-like object that persists across
                # page runs). This ensures our data is persisted when the app updates.
                st.session_state.df = df
                st.session_state.df.to_json('Data_base.json')

            # Show a section to add a new ticket
            st.header("Add an employee and worked hours")

            # We're adding tickets via an `st.form` and some input widgets. If widgets are used
            # in a form, the app will only rerun once the submit button is pressed.
            with st.form("add_ticket_form"):
                issue = st.text_area("First Name and Last Name format")
                dpto = st.selectbox("Department", ["Production", "Assembly", "Transportation", "Marketing", "Managment"])
                rates = list(range(1, 101))
                rate = st.selectbox("Hour Rate US$", rates)
                hours = st.selectbox("Worked Hours", list(range(1, 11)))

                submitted = st.form_submit_button("Submit")

            if submitted:
                # Make a DataFrame for the new ticket and append it to the DataFrame in session
                # state.
                recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                df_new = pd.DataFrame(
                    [
                        {
                            "ID": f"Payroll-{recent_ticket_number + 1}",
                            "Employee": issue,
                            "Status": "Unpaid",
                            "Department": dpto,
                            "Hour Rate": rate,
                            "Total Hours": hours,
                            "Date Submitted": today,
                        }
                    ]
                )

                # Show a little success message
                st.write("Employee Submitted! Here are the ticket details:")
                st.dataframe(df_new, use_container_width=True, hide_index=True)
                st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

                # Ensure the DataFrame index is unique before exporting to JSON
                st.session_state.df.reset_index(drop=True, inplace=True)
                st.session_state.df.to_json('Data_base.json')

            # Show section to view and edit existing tickets in a table
            st.header("Existing payrolls")
            st.write(f"Number of payrolls: `{len(st.session_state.df)}`")

            st.info(
                "You can edit the payrolls by double-clicking on a cell. Note how the plots below "
                "update automatically! You can also sort the table by clicking on the column headers.",
                icon="✍️",
            )

            # Show the tickets DataFrame with `st.data_editor`. This lets the user edit the table
            # cells. The edited data is returned as a new DataFrame.
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
                        options=list(range(1, 101)),
                        required=True,
                    ),
                },
                # Disable editing the ID and Date Submitted columns
                disabled=["ID", "Date Submitted"],
            )

            # Show some metrics and charts about the tickets
            st.header("Statistics")

            # Show metrics side by side using `st.columns` and `st.metric`
            col1, col2, col3 = st.columns(3)
            num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Unregistered"])
            col1.metric(label="Number of open payrolls", value=num_open_tickets, delta=10)
            col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
            col3.metric(label="Average resolution time (hours)", value=16, delta=2)

            # Show two Altair charts using `st.altair_chart`
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
        else:
            st.error("Invalid username or password. Please try again.")

else:
    st.success(f"Welcome back, {st.session_state['username']}!")
    # Main app content goes here
    st.write("This is the main app content.")
    # Load the existing DataFrame from the JSON file

    df = pd.read_json('Data_base.json')
    st.session_state.df = df

    # Create a random Pandas DataFrame with existing tickets
    if "df" not in st.session_state:
        # Set seed for reproducibility
        np.random.seed(42)

        # Make up some fake issue descriptions
        names = [f"Employee {i}" for i in range(20)]
        issue_descriptions = names

        # Generate the DataFrame with 5 rows/tickets
        data = {
            "ID": [f"Payroll-{i}" for i in range(1100, 1095, -1)],
            "Employee": np.random.choice(issue_descriptions, size=5),
            "Status": np.random.choice(["Unregistered", "In Progress", "Paid"], size=5),
            "Department": np.random.choice(["Production", "Assembly", "Transportation", "Marketing", "Managment"], size=5),
            "Hour Rate": np.random.choice(["1", "2", "3"], size=5),
            "Total Hours": np.random.choice(["100", "100", "100"], size=5),
            "Date Submitted": [
                datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
                for _ in range(5)
            ],
        }
        df = pd.DataFrame(data)
        # Save the DataFrame in session state (a dictionary-like object that persists across
        # page runs). This ensures our data is persisted when the app updates.
        st.session_state.df = df
        st.session_state.df.to_json('Data_base.json')

    # Show a section to add a new ticket
    st.header("Add an employee and worked hours")

    # We're adding tickets via an `st.form` and some input widgets. If widgets are used
    # in a form, the app will only rerun once the submit button is pressed.
    with st.form("add_ticket_form"):
        issue = st.text_area("First Name and Last Name format")
        dpto = st.selectbox("Department", ["Production", "Assembly", "Transportation", "Marketing", "Managment"])
        rates = list(range(1, 101))
        rate = st.selectbox("Hour Rate US$", rates)
        hours = st.selectbox("Worked Hours", list(range(1, 11)))

        submitted = st.form_submit_button("Submit")

    if submitted:
        # Make a DataFrame for the new ticket and append it to the DataFrame in session
        # state.
        recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        df_new = pd.DataFrame(
            [
                {
                    "ID": f"Payroll-{recent_ticket_number + 1}",
                    "Employee": issue,
                    "Status": "Unpaid",
                    "Department": dpto,
                    "Hour Rate": rate,
                    "Total Hours": hours,
                    "Date Submitted": today,
                }
            ]
        )

        # Show a little success message
        st.write("Employee Submitted! Here are the ticket details:")
        st.dataframe(df_new, use_container_width=True, hide_index=True)
        st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

        # Ensure the DataFrame index is unique before exporting to JSON
        st.session_state.df.reset_index(drop=True, inplace=True)
        st.session_state.df.to_json('Data_base.json')

    # Show section to view and edit existing tickets in a table
    st.header("Existing payrolls")
    st.write(f"Number of payrolls: `{len(st.session_state.df)}`")

    st.info(
        "You can edit the payrolls by double-clicking on a cell. Note how the plots below "
        "update automatically! You can also sort the table by clicking on the column headers.",
        icon="✍️",
    )

    # Show the tickets DataFrame with `st.data_editor`. This lets the user edit the table
    # cells. The edited data is returned as a new DataFrame.
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
                options=list(range(1, 101)),
                required=True,
            ),
        },
        # Disable editing the ID and Date Submitted columns
        disabled=["ID", "Date Submitted"],
    )

    # Show some metrics and charts about the tickets
    st.header("Statistics")

    # Show metrics side by side using `st.columns` and `st.metric`
    col1, col2, col3 = st.columns(3)
    num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Unregistered"])
    col1.metric(label="Number of open payrolls", value=num_open_tickets, delta=10)
    col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
    col3.metric(label="Average resolution time (hours)", value=16, delta=2)

    # Show two Altair charts using `st.altair_chart`
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

    
    # Logout button
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.experimental_rerun()  # Refresh the app to return to the login screen
