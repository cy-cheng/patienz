import streamlit as st 

# with emoji titles
@st.dialog("歡迎 🎉")
def welcome():
    st.write("歡迎使用本系統")
    st.write("您可以在左邊的選單選取不同的功能")
    st.write("請先完成病患設定並開始看診模擬")
    if st.button("開始"):
        st.switch_page("page/config.py")

@st.dialog("錯誤 ❌")
def has_config():
    st.write("您已經完成設定了")
    if st.button("確認"):
        st.switch_page("page/test.py")

@st.dialog("錯誤 ❌")
def no_config():
    st.write("您尚未完成設定")
    if st.button("確認"):
        st.switch_page("page/config.py")

@st.dialog("錯誤 ❌")
def diagnostic_ended():
    st.write("您已經完成問診了")
    if st.button("確認"):
        st.switch_page("page/grade.py")

