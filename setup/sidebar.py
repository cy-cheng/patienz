import streamlit as st 

def patient_info():
    with st.sidebar:
        st.header("病患資料設定")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        age = st.slider("年齡", 0, 100, 45)

    with col2:
        sex = st.radio("性別", ["隨機", "男", "女"])

    field = st.text_input("科別", "隨機")

def note():
    with st.sidebar:
        st.header("筆記區")
        user_notes = st.text_area("在此輸入您看診時的記錄，不計分", height=450)
