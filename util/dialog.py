import streamlit as st 

# with emoji titles
@st.dialog("歡迎 👋")
def welcome():
    st.write("歡迎使用本系統")
    st.write("您可以在左邊的選單選取不同的功能")
    st.write("請先完成病患設定並開始看診模擬")
    if st.button("開始"):
        st.switch_page("page/config.py")

@st.dialog("問診開始 🩺")
def start_test():
    st.write("在問診初步結束後，您可以利用檢查區進行進一步的檢查")
    st.write("在確認您的答案後，請在下方留下您的診斷並送出")
    st.write("在病患思考問題回答時請勿切換分頁")

@st.dialog("錯誤 ❌")
def error(e, dest=None):
    st.write(e)
    if dest:
        if st.button("確認"):
            st.switch_page(f"page/{dest}.py")

@st.dialog("存檔成功 ✅")
def config_saved(file_name: str):
    st.write(f"本次病患之設定已儲存為：")
    st.write(file_name)
    if st.button("確認"):
        st.switch_page("page/grade.py")

@st.dialog("完成問診 ✅")
def refresh():
    st.write("恭喜您完成了本次的問診")
    st.write("請點擊「確認」以重新開始")

    if st.button("確認"):
        for key in st.session_state:
            print(f"Deleting {key}")
            del st.session_state[key]
        st.session_state.first_entry = False
        st.switch_page("page/config.py")
