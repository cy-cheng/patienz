import streamlit as st
from model.patient import create_patient_model
from util.process import process_audio
import util.dialog as dialog
import util.tools as util
import util.chat as chat

# Configure instruction file paths
ss = st.session_state

util.init(3)
util.note()

column = st.columns([1, 10, 1, 4])

with column[1]:
    st.header("對話區")
    output_container = st.container()
    chat_area = output_container.empty()

    if "diagnostic_messages" not in ss:
        ss.diagnostic_messages = []

    if "clear_prompt" not in ss:
        ss.clear_prompt = False 
        
    if audio := st.audio_input("語音輸入"):
        ss.audio = audio
        ss.prompt = process_audio(audio)
        ss.prompt = st.text_area("請輸入您的對話內容", value=ss.prompt, key="prompt_area")

    chat.update(chat_area, msgs=ss.diagnostic_messages, height=200, show_all=False)

    if "audio" not in ss:
        if ss.clear_prompt:
            ss.prompt = st.text_area("請輸入您的對話內容", value="", key="prompt_area")
            ss.clear_prompt = False
        else:
            ss.prompt = st.text_area("請輸入您的對話內容", value=ss.get("prompt_area", ""), key="prompt_area")

    if st.button("送出對話", use_container_width=True) and util.check_progress():
        if ss.prompt != "":
            ss.prompt = ss.prompt.rstrip("\n")
            util.record(ss.log, f"Doctor: {ss.prompt}")

            chat.append(ss.diagnostic_messages, "doctor", ss.prompt)
            chat.update(chat_area, msgs=ss.diagnostic_messages, height=200, show_all=False)
            
            response = ss.patient.send_message(f"醫學生：{ss.prompt}")
            formatted_response = response.text.replace("(", "（").replace(")", "）")
            util.record(ss.log, f"Patient: {response.text}")
            chat.append(ss.diagnostic_messages, "patient", formatted_response)
            chat.update(chat_area, msgs=ss.diagnostic_messages, height=200, show_all=False)
            
            ss.clear_prompt = True
            st.rerun()

    ss.diagnosis = st.text_input("主診斷")
    
    ss.ddx = st.text_input("鑑別診斷（以逗號分隔）")

    ss.treatment = st.text_input("處置（包含進行之檢查與治療方式，以逗號分隔）")

# Add a confirm answer button outside the input container
    button_container = st.container()
    with button_container:
        if st.button("開始評分", use_container_width=True) and util.check_progress():
            if ss.diagnosis != "" and ss.treatment != "":
                print(ss.diagnosis)
                print(ss.treatment)
                ss.diagnostic_ended = True

                util.next_page()
            else:
                st.warning("請先完成診斷和處置")

with column[3]:
    util.show_patient_profile()

