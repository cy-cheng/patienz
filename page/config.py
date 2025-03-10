import streamlit as st 
from model.problem_setter import create_problem_setter_model
import util.dialog as dialog
import util.tools as util
import os
import random
import json
import datetime

ss = st.session_state

util.init(0)

config = {
    "年齡": None,
    "性別": None,
    "疾病領域": None,
    "疾病": None,
}

major_column = st.columns([2, 8, 2])

with major_column[1]:
    st.header("病患資訊設定")
    
    ss.config_type = st.radio("選擇設定方式", ["模板題", "輸入參數", "題目存檔"], horizontal=True)

    if ss.config_type == "輸入參數":
        minor_column_1 = st.columns([10, 1, 10])
        with minor_column_1[0]:
            config["年齡"] = st.slider("年齡（隨機區間）", 15, 100, (15, 100))

        with minor_column_1[2]:
            config["性別"] = st.radio("性別", ["隨機", "男", "女"], horizontal=True)

        field_options = ["心臟", "胸腔", "腸胃"]

        config["疾病領域"] = st.selectbox("疾病領域", ["隨機"] + field_options)

        config["疾病"] = st.text_input("疾病", "隨機")
    elif ss.config_type == "模板題":
        problem_set = os.listdir("data/template_problem_set/")
        problem = st.selectbox("模板題選單", sorted(problem_set), index=None)
    elif ss.config_type == "題目存檔":
        problem_set = os.listdir("data/problem_set/")
        problem = st.selectbox("過去練習記錄", problem_set, index=None)

    if st.button("確認設定並開始看診", use_container_width=True) and util.check_progress():
        if "problem" in ss:
            dialog.error("請先完成目前的題目", "test")
            pass
        elif ss.config_type == "輸入參數":
            config["年齡"] = random.randint(config["年齡"][0], config["年齡"][1])

            if config["性別"] == "隨機":
                config["性別"] = random.choice(["男", "女"])

            if config["疾病領域"] == "隨機":
                config["疾病領域"] = random.choice(field_options)
        elif ss.config_type == "模板題":
            with open(f"data/template_problem_set/{problem}", "r") as f:
                ss.problem = f.read()
            print(f"Problem: {problem}")
            ss.data = json.loads(ss.problem) 

            util.next_page()
        else:
            with open(f"data/problem_set/{problem}", "r") as f:
                ss.problem = f.read()
            print(f"Problem: {problem}")
            ss.data = json.loads(ss.problem) 

            util.next_page()

        ss.user_config = config

# Initialize models in session state
if "problem_setter_model" not in ss:
    create_problem_setter_model()

if "user_config" in ss and "problem" not in ss:
    config = "\n".join([f"{key}: {value}" for key, value in ss.user_config.items()])
    ss.problem = ss.problem_setter.send_message(f"請利用以下資訊幫我出題：\n今日日期：{datetime.datetime.now().strftime('%Y/%m')} （年/月）\n{config}").text

    print(f"請利用以下資訊幫我出題：\n今日日期：{datetime.datetime.now().strftime('%Y/%m')} （年/月）\n{config}")
    ss.data = json.loads(ss.problem) 
    util.record(ss.log, config)

    util.record(ss.log, ss.problem)

    util.next_page()
