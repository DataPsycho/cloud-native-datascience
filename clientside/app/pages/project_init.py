import re
import typing as t
from dataclasses import dataclass

import streamlit as st
from app.domains.project import PostProjectPayload
from app.usecases.projects import create_project

DESC = (
    "*Using this form you can create a project, which you can use while submitting a document. "
    "The project history can be viewed in the History tab*"
)


@dataclass
class Result:
    success: t.Optional[bool] = True
    error: t.Optional[str] = None


def validate_input(user_input: str):
    regexp = re.compile('[^0-9a-zA-Z]+')
    special_char = regexp.findall(user_input.replace(" ", ""))
    if len(special_char) > 0:
        combined_char = " ".join(special_char)
        error = f"ValidationError: Following special character are in the input: {combined_char}"
        return Result(success=False, error=error)
    return Result()


def main():
    st.header("Create a Project for Document Submission")
    st.markdown(f"{DESC}")
    with st.form("project_form"):
        project_name = st.text_input("Project Name*")
        submitted = st.form_submit_button("Submit")

    if submitted:
        result = validate_input(project_name)
        if result.success:
            payload = PostProjectPayload(name=project_name)
            project = create_project(payload=payload)
            st.markdown(f"🎉 Following project has been created successfully: __{project.SK}__")
        else:
            st.markdown(result.error)
