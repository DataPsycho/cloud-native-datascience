import streamlit as st
from app.usecases.projects import get_project_as_table

DESC = (
    "*Submit request to generate project history.*"
)


def main():
    st.header("View Project History")
    st.markdown(DESC)
    submitted = st.button("Submit")
    if submitted:
        table = get_project_as_table()
        st.table(table)

