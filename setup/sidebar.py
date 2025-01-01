import streamlit as st 
import random



def note():
    with st.sidebar:
        st.header("筆記區")
        st.text_area("在此輸入您看診時的記錄，不計分", height=350)

        if "user_config" in st.session_state: st.markdown(str(st.session_state.user_config))

