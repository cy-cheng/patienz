import streamlit as st
from model.patient import create_patient_model
import json

# Configure instruction file paths
PATIENT_INSTRUCTION = "instruction_file/patient_instruction.txt"

# Initialize models in session state
if "patient_model" not in st.session_state and "problem" in st.session_state:
    patient_model = create_patient_model(PATIENT_INSTRUCTION, st.session_state.problem)
    st.session_state.patient_model = patient_model
    st.session_state.patient = st.session_state.patient_model.start_chat()

# sidebar 
with st.sidebar:
    st.header("筆記區")
    st.text_area("在此輸入您看診時的記錄，不計分", height=350)

column = st.columns([2, 8, 1, 3])

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

    input_container = st.container()
    with input_container:
        if prompt := st.chat_input("輸入您對病人的話", key="user_input"):
            st.session_state.diagnostic_messages.append({"role": "doctor", "content": prompt})
            update_chat_history()
            
            response = st.session_state.patient.send_message(f"醫生：{prompt}")
            st.session_state.diagnostic_messages.append({"role": "patient", "content": response.text})
            update_chat_history()

# Add a confirm answer button outside the input container
    button_container = st.container()
    with button_container:
        if st.button("完成問診"):
            st.session_state.diagnostic_ended = True
            st.switch_page("page/grade.py")

with column[3]:
    st.header("病人資料")
    data_container = st.container(height=350)
    if "data" in st.session_state:
        with data_container:
            basic_info = st.session_state.data["基本資訊"]
            st.write(f"姓名：{basic_info['姓名']}")
            st.write(f"年齡：{basic_info['年齡']}")
