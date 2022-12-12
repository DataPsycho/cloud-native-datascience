import logging

import streamlit as st
from app.domains.jobs import GetJobStatusPayload
from app.usecases.jobs import get_jobs_as_table
from app.usecases.projects import get_project_as_list

DESC = (
    "*View the job status for any selected project. "
    "You can filter to see the specific status for a particular "
    "project.*"
)


def main():
    st.header("View Job Status")
    st.markdown(DESC)
    status_opt = ["all", 'running', 'completed', 'failed', 'rejected']
    with st.form("show_job_form"):
        projects = get_project_as_list()
        selected_project = st.selectbox("Select Project*", projects)
        status_type = st.selectbox(label="Select Status*", options=status_opt)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if selected_project != "---":
            try:
                payload = GetJobStatusPayload(pid=selected_project, status=status_type)
                result = get_jobs_as_table(payload=payload)
                st.markdown("Here is the list of job status.")
                st.table(result)
            except Exception as e:
                logging.info(e)
                st.markdown("ClientError: No job status found for the project.")
