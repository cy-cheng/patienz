import streamlit as st
from model.patient import create_patient_model
from util.process import process_audio
import util.dialog as dialog
import util.tools as util
import json
import time 

# Configure instruction file paths
PATIENT_INSTRUCTION = "instruction_file/patient_instruction.txt"
ss = st.session_state

# first test entry

if "first_test_entry" not in ss and "first_entry" in ss:
    ss.first_test_entry = False
    dialog.start_test()

# sidebar 

if "note" not in ss:
    ss.note = ""

with st.sidebar:
    st.header("筆記區")
    ss.note = st.text_area("在此輸入您看診時的記錄，不計分", height=350, value=ss.note)

column = st.columns([1, 10, 1, 4])

with column[1]:
    st.header("對話區")
    output_container = st.container()
    chat_area = output_container.empty()

    if "diagnostic_messages" not in ss:
        ss.diagnostic_messages = []

    avatar_map = {
        "doctor": "⚕️",
        "patient": "😥",
        "grader": "🏫"
    }

    def update_chat_history():
        chat_area.empty()
        with chat_area.container(height=200):
            if "diagnostic_ended" in ss:
                for msg in ss.diagnostic_messages:
                    with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
                        st.markdown(msg["content"])
            else:
                for msg in ss.diagnostic_messages[-2:]:
                    try:
                        with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
                            st.markdown(msg["content"])
                    except:
                        pass

    update_chat_history()

    if "patient_model" not in ss and "problem" in ss:
        create_patient_model(PATIENT_INSTRUCTION, ss.problem)
    
    if audio := st.audio_input("語音輸入"):
        ss.audio = audio
        ss.prompt = process_audio(audio)
        ss.prompt = st.text_area("請輸入您的對話內容", value=ss.prompt)

    if "audio" not in ss:
        ss.prompt = st.text_area("請輸入您的對話內容")

    if st.button("送出對話", use_container_width=True):
        if "patient_model" not in ss:
            dialog.error("請先完成病患設定", "config")
        elif "diagnostic_ended" in ss:
            dialog.error("本次問診已結束", "grade")
        elif ss.prompt != "":
            ss.prompt = ss.prompt.rstrip("\n")
            ss.diagnostic_messages.append({"role": "doctor", "content": ss.prompt})
            update_chat_history()

            response = ss.patient.send_message(f"醫學生：{ss.prompt}")
            formatted_response = response.text.replace("(", "（").replace(")", "）")
            ss.diagnostic_messages.append({"role": "patient", "content": formatted_response})
            update_chat_history()

    ss.diagnosis = st.text_input("主診斷")
    
    ss.ddx = st.text_input("鑑別診斷（以逗號分隔）")

    ss.treatment = st.text_input("處置（包含進行之檢查與治療方式，以逗號分隔）")

# Add a confirm answer button outside the input container
    button_container = st.container()
    with button_container:
        if st.button("完成問診", use_container_width=True):
            if ss.diagnosis != "" and ss.treatment != "":
                print(ss.diagnosis)
                print(ss.treatment)
                ss.diagnostic_ended = True
                st.switch_page("page/grade.py")
            else:
                st.warning("請先完成診斷和處置")

with column[3]:
    st.header("病人資料")
    data_container = st.container(border=True)
    if "data" in ss:
        data = ss.data
        with data_container:
            st.write(f"姓名：{data['基本資訊']['姓名']}")
            st.write(f"生日：{data['基本資訊']['生日']}")
            # st.write(f"年齡：{data['基本資訊']['年齡']}")
            st.write(f"性別：{data['基本資訊']['性別']}")
            st.write(f"身高：{data['基本資訊']['身高']} cm")
            st.write(f"體重：{data['基本資訊']['體重']} kg")

