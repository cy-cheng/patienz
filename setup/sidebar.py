import streamlit as st 
import random

@st.dialog("選擇病患資訊")
def open_config():
    config = {
        "年齡": None,
        "性別": None,
        "疾病科別": None,
        "疾病": None,
        "病史": None,
    }

    col1, col2 = st.columns(2)

    with col1:
        config["年齡"] = st.slider("年齡", 0, 100, (0, 100))

    with col2:
        config["性別"] = st.radio("性別", ["隨機", "男", "女"])

    field_options = ["心臟科", "神經科", "骨科", "內科", "外科", "婦產科", "小兒科", "眼科", "耳鼻喉科", "皮膚科", "泌尿科"]
    # make a selct with a random option

    config["疾病科別"] = st.selectbox("疾病科別", ["隨機"] + field_options)

    config["疾病"] = st.text_input("疾病", "隨機")
    config["病史"] = st.text_input("病史", "隨機")

    if st.button("確定"):
        config["年齡"] = random.randint(config["年齡"][0], config["年齡"][1])

        if config["性別"] == "隨機":
            config["性別"] = random.choice(["男", "女"])

        if config["疾病科別"] == "隨機":
            config["疾病科別"] = random.choice(field_options)

        st.session_state.user_config = config
        st.rerun()


def patient_info():
    if "enter_app" not in st.session_state:
        st.session_state.enter_app = True
        open_config()

    with st.sidebar:
        if "user_config" not in st.session_state:
            if st.button("設定病患資訊"):
                open_config()

def note():
    with st.sidebar:
        st.header("筆記區")
        st.text_area("在此輸入您看診時的記錄，不計分", height=450)

        if "user_config" in st.session_state: st.markdown(str(st.session_state.user_config))

