import streamlit as st
from model.patient import create_patient_model
from util.process import process_audio
import util.tools as util
import util.chat as chat
import time 

# Configure instruction file paths
ss = st.session_state

util.init(1)
util.note()

column = st.columns([1, 10, 1, 4])

with column[1]:
    st.header("對話區")
    output_container = st.container()
    chat_area = output_container.empty()

    chat.update(chat_area, msgs=ss.diagnostic_messages, height=200, show_all=ss.show_all)

    if ss.current_progress == 1 and "patient_model" not in ss:
        create_patient_model(ss.problem)

    if audio := st.audio_input("語音輸入"):
        ss.audio = audio
        ss.prompt = process_audio(audio)
        ss.prompt = st.text_area("請輸入您的對話內容", value=ss.prompt)

    if "audio" not in ss:
        ss.prompt = st.text_area("請輸入您的對話內容")

    if st.button("送出對話", use_container_width=True) and util.check_progress():
        if ss.prompt != "":
            ss.prompt = ss.prompt.rstrip("\n")
            util.record(ss.log, f"Doctor: {ss.prompt}")

            chat.append(ss.diagnostic_messages, "doctor", ss.prompt)
            chat.update(chat_area, msgs=ss.diagnostic_messages, height=200, show_all=ss.show_all)
            
            response = ss.patient.send_message(f"醫學生：{ss.prompt} （請作為病人回答）")
            formatted_response = response.text.replace("(", "（").replace(")", "）")
            util.record(ss.log, f"Patient: {response.text}")

            chat.append(ss.diagnostic_messages, "patient", formatted_response) 
            chat.update(chat_area, msgs=ss.diagnostic_messages, height=200, show_all=ss.show_all)

# Add a confirm answer button outside the input container
    button_container = st.container()
    with button_container:
        if st.button("完成問診", use_container_width=True) and util.check_progress():
            ss.diagnostic_ended = True

            util.next_page()

with column[3]:
    util.show_patient_profile()

    st.subheader("其他資訊")
    with st.container(border=True):
        util.peek_chat()
        util.show_time()

