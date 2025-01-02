import streamlit as st 

st.set_page_config(layout="wide")

@st.dialog("👋 歡迎使用本系統！")
def welcome():
    st.markdown("本系統提供病患看診、評分等功能。")

pages = [
    st.Page("page/config.py", title="病患設定", icon="🔧"),
    st.Page("page/test.py", title="看診區", icon="🩺"),
    st.Page("page/grade.py", title="評分區", icon="📝"),
]

page = st.navigation(pages)
page.run()

if "first_entry" not in st.session_state:
    st.session_state.first_entry = True
    welcome()
