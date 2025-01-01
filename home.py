import streamlit as st 

pages = [
    st.Page("pages/config.py", title="config", icon="🔧"),
    st.Page("pages/test.py", title="test", icon="🩺"),
    st.Page("pages/grade.py", title="grade", icon="📝"),
]

page = st.navigation(pages)
page.run()
