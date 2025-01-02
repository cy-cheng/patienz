import streamlit as st
from model.grader import create_grader_model
import datetime
import json

GRADER_INSTRUCTION = "instruction_file/grader_inst_gpt.txt"

# Define avatar map 
avatar_map = {
    "doctor": "⚕️",
    "patient": "😥",
    "grader": "🏫"
}

column = st.columns([2, 8, 2])

with column[1]:
    st.header("對話區")
    output_container = st.container()
    chat_area = output_container.empty()

    if "grading_messages" not in st.session_state:
        st.session_state.grading_messages = []

    avatar_map = {
        "doctor": "⚕️",
        "patient": "😥",
        "grader": "🏫"
    }

    def update_chat_history():
        chat_area.empty()
        with chat_area.container(height=576):
            for msg in st.session_state.grading_messages:
                with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
                    st.markdown(msg["content"])

    update_chat_history()

    input_container = st.container()
    with input_container:
        if prompt := st.chat_input("輸入您對評分的問題", key="user_input"):
            if "grade_ended" in st.session_state:
                pass

            st.session_state.grading_messages.append({"role": "doctor", "content": prompt})
            update_chat_history()
            
            response = st.session_state.grader.send_message(f"學生：{prompt}")
            st.session_state.grading_messages.append({"role": "grader", "content": response.text})
            update_chat_history()

    button_column = st.columns([1, 1])
    with button_column[0]:
        if st.button("結束評分"):
            st.session_state.grade_ended = True

    with button_column[1]:
        if st.button("儲存本次病患設定"):
            data = st.session_state.data
            file_name = f"{datetime.datetime.now().strftime('%Y%m%d')} - {data['基本資訊']['姓名']} - {data['Problem']['疾病']}.json"

            with open(f"data/problem_set/{file_name}", "w") as f:
                f.write(st.session_state.problem)



if "diagnostic_ended" in st.session_state and len(st.session_state.grading_messages) == 0:
    grader_model = create_grader_model(GRADER_INSTRUCTION)
    st.session_state.grader_model = grader_model
    st.session_state.grader = st.session_state.grader_model.start_chat()
    chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in st.session_state.diagnostic_messages])
    
    grader_response = st.session_state.grader.send_message("以下是問診記錄：\n"+chat_history+"\n請針對此份問診給出客觀的評分")

    print(grader_response.text)

    st.session_state.grading_messages = [{"role": "grader", "content": grader_response.text}]
    update_chat_history()
    
