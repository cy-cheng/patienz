import streamlit as st 
from model.examiner import create_examiner_model
import util.dialog as dialog
import util.tools as util
import csv
import json

EXAMINER_INSTRUCTION = "instruction_file/examiner_instruction.txt"

ss = st.session_state

major_column = st.columns([2, 8, 2])

with major_column[1]:
    st.header("選擇檢查領域")

    with open("data/examination_choice.json", "r", encoding="utf-8") as f:
        examination_choice = json.load(f)

    category = st.radio("檢查領域", list(examination_choice.keys()))

    if category != None:

        examination = st.header("選擇檢查項目", list(examination_choice[category].keys()))

        if examination != None:
            l, r = examination_choice[category][examination].l, examination_choice[category][examination].r

            with open("data/examination.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                data = [row for row in reader]
                data = data[l:r]

            item = st.multiselect("選擇檢查細項", data)

            st.write(f"已選擇：{item}")




    

# Initialize models in session state
if "examiner_model" not in ss:
    create_examiner_model(EXAMINER_INSTRUCTION)

if "user_config" in ss and "problem" not in ss:
    config = "\n".join([f"{key}: {value}" for key, value in ss.user_config.items()])
    ss.problem = ss.problem_setter.send_message(f"請利用以下資訊幫我出題：\n今日日期：{datetime.datetime.now().strftime('%Y/%m/')} （年/月）\n{config}" + config).text
    ss.data = json.loads(ss.problem) 
    util.record(ss.log, config)

    util.record(ss.log, ss.problem)
    st.switch_page("page/test.py")
