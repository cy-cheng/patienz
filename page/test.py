import streamlit as st
from model.patient import create_patient_model
from util.search import search_and_export_to_pdf 
import page.dialog as dialog
import json
import time 

# Configure instruction file paths
PATIENT_INSTRUCTION = "instruction_file/patient_instruction.txt"

# sidebar 
with st.sidebar:
    st.header("筆記區")
    st.text_area("在此輸入您看診時的記錄，不計分", height=350)

column = st.columns([1, 10, 1, 4])

with column[1]:
    st.header("對話區")
    output_container = st.container()
    chat_area = output_container.empty()

    if "diagnostic_messages" not in st.session_state:
        st.session_state.diagnostic_messages = []

    avatar_map = {
        "doctor": "⚕️",
        "patient": "😥",
        "grader": "🏫"
    }

    def update_chat_history():
        chat_area.empty()
        with chat_area.container(height=350):
            if "diagnostic_ended" in st.session_state:
                for msg in st.session_state.diagnostic_messages:
                    with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
                        st.markdown(msg["content"])
            else:
                for msg in st.session_state.diagnostic_messages[-2:]:
                    try:
                        with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
                            st.markdown(msg["content"])
                    except:
                        pass

    update_chat_history()

    if "patient_model" not in st.session_state and "problem" in st.session_state:
        create_patient_model(PATIENT_INSTRUCTION, st.session_state.problem)

    if prompt := st.chat_input("輸入您對病人的話", key="user_input"):
        if "patient" not in st.session_state:
            dialog.no_config()

        elif "diagnostic_ended" in st.session_state:
            dialog.diagnostic_ended()

        else:
            st.session_state.diagnostic_messages.append({"role": "doctor", "content": prompt})
            update_chat_history()

            response = st.session_state.patient.send_message(f"醫生：{prompt}")
            st.session_state.diagnostic_messages.append({"role": "patient", "content": response.text})
            update_chat_history()

    sub_column = st.columns([1, 1])
    with sub_column[0]:
        st.session_state.diagnosis = st.text_input("診斷")
    
    with sub_column[1]:
        st.session_state.treatment = st.text_input("處置")

# Add a confirm answer button outside the input container
    button_container = st.container()
    with button_container:
        if st.button("完成問診", use_container_width=True):
            if st.session_state.diagnosis != "" and st.session_state.treatment != "":
                print(st.session_state.diagnosis)
                print(st.session_state.treatment)
                st.session_state.diagnostic_ended = True
                st.switch_page("page/grade.py")
            else:
                st.warning("請先完成診斷和處置")

with column[3]:
    st.header("病人資料")
    data_container = st.container(border=True)
    if "data" in st.session_state:
        data = st.session_state.data
        with data_container:
            st.write(f"姓名：{data['基本資訊']['姓名']}")
            st.write(f"生日：{data['基本資訊']['生日']}")
            # st.write(f"年齡：{data['基本資訊']['年齡']}")
            st.write(f"性別：{data['基本資訊']['性別']}")
            st.write(f"身高：{data['基本資訊']['身高']} cm")
            st.write(f"體重：{data['基本資訊']['體重']} kg")

