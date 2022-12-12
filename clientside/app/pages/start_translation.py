import logging

import streamlit as st
from app.domains.document import GetDocumentStatusPayload
from app.domains.jobs import PostJobPayload
from app.usecases.documents import confirm_english_document
from app.usecases.jobs import create_translation_job
from app.usecases.projects import get_project_as_list

DESC = (
    "*Please select a valid project to start a translation job"
    "You can download the translated document from the Download section. "
    "After the translation is finished.*"
)


def main():
    st.header("Start a Translation Process")
    st.markdown(DESC)
    with st.form("docx_submission_form"):
        projects = get_project_as_list()
        selected_project = st.selectbox("Select Project*", projects)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if selected_project != "---":
            try:
                payload_eng_status = GetDocumentStatusPayload(pid=selected_project)
                if confirm_english_document(payload_eng_status):
                    logging.info("English document is found!")
                    payload = PostJobPayload(sk=selected_project)
                    result = create_translation_job(payload)
                    st.markdown(
                        "🍵 Tea Time, Following job is in the queue, with JobID: "
                        f"__{result.jid}__, Version: __{result.version}__ "
                        f"check the job status on the __Job Status__ section."
                    )
                else:
                    st.markdown("ServerError: Can you trigger any job!")
            except Exception as e:
                logging.info(e)
                st.markdown("ProcessError: Problem creating job, please contact dev team.")
        else:
            st.markdown("You must need to select a valid project.")