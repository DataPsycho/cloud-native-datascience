import logging

import streamlit as st
from app.domains.document import GetGermanDocumentPayload
from app.usecases.documents import get_german_document
from app.usecases.projects import get_project_as_list
from xfilios.docx import DocxHandler

DESC = (
    "*Please select a valid project to download the translated document. "
    "You must have to submit a valid document using the Submit tab to generate "
    "a translated document.*"
)


def main():
    st.header("Download Translated Document")
    st.markdown(DESC)
    with st.form("docx_download_form"):
        projects = get_project_as_list()
        selected_project = st.selectbox("Select Project*", projects)
        submitted = st.form_submit_button("Submit")
    if submitted:
        try:
            payload = GetGermanDocumentPayload(pid=selected_project)
            result = get_german_document(payload=payload)
            handler = DocxHandler.from_base64(result.content)
            download_link = handler.create_download_link("demo-docx.docx")
            st.markdown(f"🎁 Here is your translated document: {download_link}", unsafe_allow_html=True)
        except Exception as e:
            logging.info(e)
            st.markdown(
                "SystemError: Could not download the file. "
                f"Check if you have completed translation job for the project __{selected_project}__"
            )
