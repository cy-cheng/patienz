import streamlit as st
from model.grader import create_grader_model
import datetime
import json

GRADER_INSTRUCTION_FOLDER = "instruction_file/"

# Define avatar map 
avatar_map = {
    "doctor": "⚕️",
    "patient": "😥",
    "grader": "🏫"
}

column = st.columns([1, 10, 2])

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
        # chat_area.empty()
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
        if st.button("結束評分", use_container_width=True):
            st.session_state.grade_ended = True

    with button_column[1]:
        if st.button("儲存本次病患設定", use_container_width=True):
            data = st.session_state.data
            file_name = f"{datetime.datetime.now().strftime('%Y%m%d')} - {data['基本資訊']['姓名']} - {data['Problem']['疾病']}.json"

            with open(f"data/problem_set/{file_name}", "w") as f:
                f.write(st.session_state.problem)

def getGradingResult(current_model, messages_for_grading):
    st.session_state.grader_model = current_model
    st.session_state.grader = st.session_state.grader_model.start_chat()
    return st.session_state.grader.send_message(messages_for_grading)

def processGradingResult(_input): # call after .text
    grading_result = json.loads(_input)
    sorted_result = sorted(grading_result, key=lambda x: (x['id']))

    grades = "|評分項目|配分|得分|回饋|\n|:---:|:---:|:---:|:---:|\n"
    full_score = 0
    real_score = 0

    for data in sorted_result:
        full_score += int(data['full_score'])
        real_score += int(data['real_score'])
        grades += (f"|{data['item']}|{data['full_score']}|{data['real_score']}|{data['feedback']}|\n")

    grades += (f"|總分|{full_score}|得分|{real_score}|\n\n")

    return grades


if "diagnostic_ended" in st.session_state and len(st.session_state.grading_messages) == 0:
    # Initialize grader models
    grader_models = []
    for i in range(5):
        grader_models.append(create_grader_model(GRADER_INSTRUCTION_FOLDER+"grader_inst_"+chr(65+i)+".txt")) # A to E
    
    # Process chat history and some info
    chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in st.session_state.diagnostic_messages])
    
    test_answer_json = st.session_state.data
    test_answer = f"正確病症：{test_answer_json["Problem"]["疾病"]}"
    
    st.session_state.grading_messages = [{"role": "grader", "content": test_answer}]
    update_chat_history()
    
    answer_for_grader = f"以下JSON記錄的為正確診斷與病人資訊：\n{test_answer_json}\n"
    
    # Grading...
    grader_responses = []
    grading_results = []
    for i in range(5):
        if i <= 2:
            grader_responses.append(getGradingResult(grader_models[i],"以下是問診記錄：\n"+chat_history+"\n請針對此份問診給出客觀的評分"))
        else:
            grader_responses.append(getGradingResult(grader_models[i],answer_for_grader+"以下是問診記錄：\n"+chat_history+"\n請針對此份問診給出客觀的評分"))
        grading_results.append(processGradingResult(grader_responses[i].text))
    
    # Merge grading results
    grading_result = ""
    for i in range(5):
        grading_result += grading_results[i]

    st.session_state.grading_messages.append({"role": "grader", "content": grading_result})
    update_chat_history()


