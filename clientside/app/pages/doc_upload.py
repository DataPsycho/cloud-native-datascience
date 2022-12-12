import streamlit as st
from app.domains.document import PostEnglishDocPayload
from app.usecases.documents import save_english_document
from app.usecases.projects import get_project_as_list
from xfilios.docx import DocxHandler, ReadDocFunc

DESC = (
    "*Please select a valid project and upload your document. "
    "You document will be validated after upload. "
    "If your project has a document added it will be overwritten."
    "Overwritten document can not be reverted back at the moment.*"
)


def main():
    st.header("Submit Document for a Project")
    st.markdown(DESC)
    with st.form("docx_submission_form"):
        projects = get_project_as_list()
        selected_project = st.selectbox("Select Project*", projects)
        # selected_project = "test-02-2022-12-12T12:58:44"
        content = st.file_uploader("Upload Docx File*", type="docx")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if selected_project != "---" and content:
            docx_handler = DocxHandler.from_file_like(content=content)
            payload = PostEnglishDocPayload(
                sk=selected_project,
                doc=content.name,
                data=docx_handler.to_base64_str(),
            )
            result = save_english_document(payload)
            st.markdown(f":tada: Document added successfully for project __{result.SK}__.")

        else:
            st.markdown(
                "Can not submit your request, "
                "The form data you have submitted is malformed. "
                "Or Project is not selected properly"
            )
