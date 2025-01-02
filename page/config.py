import streamlit as st 
from model.problem_setter import create_problem_setter_model
import os
import random
import json

PROBLEM_SETTER_INSTRUCTION = "instruction_file/problem_setter_instruction.txt"

config = {
    "年齡": None,
    "性別": None,
    "疾病科別": None,
    "疾病": None,
    "病史": None,
}

major_column = st.columns([2, 8, 2])

with major_column[1]:
    st.title("病患資訊設定")
    
    st.session_state.config_type = st.radio("選擇設定方式", ["輸入參數", "模板題", "題目存檔"])

    if st.session_state.config_type == "輸入參數":
        minor_column_1 = st.columns([1, 1])
        with minor_column_1[0]:
            config["年齡"] = st.slider("年齡（隨機區間）", 0, 100, (0, 100))

        with minor_column_1[1]:
            config["性別"] = st.radio("性別", ["隨機", "男", "女"])

        field_options = ["心臟科", "神經科", "骨科", "內科", "外科", "婦產科", "小兒科", "眼科", "耳鼻喉科", "皮膚科", "泌尿科"]
# make a selct with a random option

        config["疾病科別"] = st.selectbox("疾病科別", ["隨機"] + field_options)

        config["疾病"] = st.text_input("疾病", "隨機")
        config["病史"] = st.text_input("病史", "隨機")
    elif st.session_state.config_type == "模板題":
        problem_set = os.listdir("data/problem_set/")
        problem = st.selectbox("模板題選單", problem_set, index=None)
    elif st.session_state.config_type == "題目存檔":
        problem_set = os.listdir("data/problem_set/")
        problem = st.selectbox("過去練習記錄", problem_set, index=None)

    if st.button("確定"):
        if st.session_state.config_type == "輸入參數":
            config["年齡"] = random.randint(config["年齡"][0], config["年齡"][1])

            if config["性別"] == "隨機":
                config["性別"] = random.choice(["男", "女"])

            if config["疾病科別"] == "隨機":
                config["疾病科別"] = random.choice(field_options)
        else:
            with open(f"data/problem_set/{problem}", "r") as f:
                problem = f.read()
            st.switch_page("page/test.py")
            st.session_state.data = json.loads(st.session_state.problem) 

        st.session_state.user_config = config

# Initialize models in session state
if "problem_setter_model" not in st.session_state:
    problem_setter_model = create_problem_setter_model(PROBLEM_SETTER_INSTRUCTION)
    st.session_state.problem_setter_model = problem_setter_model
    st.session_state.problem_setter = st.session_state.problem_setter_model.start_chat()

if "user_config" in st.session_state and "problem" not in st.session_state:
    config = "\n".join([f"{key}: {value}" for key, value in st.session_state.user_config.items()])
    st.session_state.problem = st.session_state.problem_setter.send_message("請利用以下資訊幫我出題：\n" + config).text
    st.session_state.data = json.loads(st.session_state.problem) 

    print(st.session_state.problem)
    st.switch_page("page/test.py")
