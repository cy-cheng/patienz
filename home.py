import streamlit as st 
import util.dialog as dialog

st.set_page_config(layout="wide")

pages = [
    st.Page("page/config.py", title="病患設定", icon="🔧"),
    st.Page("page/test.py", title="看診區", icon="🩺"),
    st.Page("page/examination.py", title="檢查區", icon="🧪"),
    st.Page("page/grade.py", title="評分區", icon="📝"),
]

page = st.navigation(pages)
page.run()

if "first_entry" not in st.session_state:
    st.session_state.first_entry = False
    dialog.welcome()
