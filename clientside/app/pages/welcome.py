import logging

import streamlit as st

WELCOME_SPEECH = """
The app can be used to translate English document into German.

### Submission Guideline:
- First you have to create a project using the __Create Project__ section
- Then you can navigate to the __Add Document__ tab and submit the document by selecting the project you have created
- Next, you can navigate to the __Start Translation__ section and initiate the translation process

### Other Tabs:
- The status of the translation can be viewed in the Job Status tab
- History about your project can be viewed in the History tab

### File Format Support:
- The document have to be submitted as __Microsoft Docx__ file format
- Only paragraph of text is allowed at the moment, any table submission will be Failed
"""


def main() -> None:
    welcome_text = " 🦆 Quack 🦆🐾"
    st.header(welcome_text)
    st.subheader("Your Translation Buddy")
    st.markdown(WELCOME_SPEECH)
    with st.sidebar:
        st.markdown("---")
        uid = st.sidebar.text_input("UserName", value="", type="password")
        pin = st.sidebar.text_input("PIN", value="", type="password")
        if uid and pin:
            logging.info(uid)
            logging.info(pin)
