import logging
import sys


import streamlit as st
from app.pages import (
    doc_download, doc_upload, history, job_status,
    project_init, start_translation, welcome
)

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

radio_button_factory = {
    " 🚩 Welcome": {"func": welcome.main, 'activate': True},
    " 🔁 Create Project": {"func": project_init.main, 'activate': True},
    " 🔁 Add Document": {"func": doc_upload.main, 'activate': True},
    " 🔁 Start Translation": {"func": start_translation.main, 'activate': True},
    " 🔁 Download Translation": {"func": doc_download.main, 'activate': True},
    " 🔁 Project History": {"func": history.main, 'activate': True},
    " 🔁 Job Status": {"func": job_status.main, 'activate': True},

}


def create_app() -> None:
    """
    Create the main app from the page repository
    :return: No Return
    """
    active_sections = {key: value for key, value in radio_button_factory.items() if value['activate']}
    sorted(active_sections)
    st.sidebar.header(":open_book: Menu")
    option = st.sidebar.radio("", list(active_sections.keys()))

    func = active_sections[option]["func"]
    func()  # type: ignore


if __name__ == "__main__":
    create_app()
