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

column = st.columns([1, 20, 2])

with column[1]:
    st.header("評分結果")

    tab = st.tabs([ f"分項 {chr(65+i)}" for i in range(5)])
    output_container = st.container()
    chat_area = output_container.empty()

    for i in range(5):
        with tab[i]:
            st.subheader(f"分項 {chr(65+i)}")


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
                    st.markdown(msg["content"], unsafe_allow_html=True)

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

# Scores
total_scores = 0
gotten_scores = 0

def processGradingResult(_input, ctrl): # call after .text
    global total_scores
    global gotten_scores

    grading_result = json.loads(_input)
    sorted_result = sorted(grading_result, key=lambda x: (x['id']))

    grades = ""
    
    open_str = "<th style=\"white-space: nowrap;\">"
    
    if ctrl != 0:
        grades += "<tr>\n"
        grades += f"{open_str}***</th>\n"
        grades += f"{open_str}***</th>\n"
        grades += f"{open_str}***</th>\n"
        grades += f"{open_str}***</th>\n"
        grades += "</tr>\n"
    
    grades += "<tr>\n"
    grades += f"{open_str}第{ctrl+1}類評分項目</th>\n"
    grades += f"{open_str}回饋</th>\n"
    grades += f"{open_str}得分</th>\n"
    grades += f"{open_str}配分</th>\n"
    grades += "</tr>\n"
    
    full_score = 0
    real_score = 0

    for data in sorted_result:
        full_score += int(data['full_score'])
        real_score += int(data['real_score'])

        grades += "<tr>\n"
        grades += f"{open_str}{data['item']}</th>\n"
        grades += f"{open_str}{data['feedback']}</th>\n"
        grades += f"{open_str}{data['real_score']}</th>\n"
        grades += f"{open_str}{data['full_score']}</th>\n"
        grades += "</tr>\n"

    grades += "<tr>\n"
    grades += f"{open_str}類別總分</th>\n"
    grades += f"{open_str}{full_score}</th>\n"
    grades += f"{open_str}類別得分</th>\n"
    grades += f"{open_str}{real_score}</th>\n"
    grades += "</tr>\n"

    total_scores += full_score
    gotten_scores += real_score

    return grades

if "diagnostic_ended" in st.session_state and len(st.session_state.grading_messages) == 0:
    # Initialize grader models
    grader_models = []
    for i in range(5):
        grader_models.append(create_grader_model(GRADER_INSTRUCTION_FOLDER+"grader_inst_"+chr(65+i)+".txt")) # A to E
    
    # Process chat history and some info
    chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in st.session_state.diagnostic_messages])
    chat_history += f"\n特別注意：**以下是實習醫師的診斷結果：{st.session_state.diagnosis}**"
    chat_history += f"\n特別注意：**以下是實習醫師的判斷處置：{st.session_state.treatment}**"

    print(chat_history)
    
    test_answer_json = st.session_state.data
    test_answer = f'正確病症：{test_answer_json["Problem"]["疾病"]}'
    
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
        
        grading_results.append(processGradingResult(grader_responses[i].text, i))

    # Merge grading results
    grading_result = "<table style=\"width:100%; border-collapse: collapse;\">\n"

    for i in range(5):
        grading_result += grading_results[i]
    grading_result += "</table>\n"
    grading_result += f"<p style='margin-top: 20px;'>得分率：{round(gotten_scores/total_scores*1000)/10}%。</p>\n"

    # print(grading_result)

    st.session_state.grading_messages.append({"role": "grader", "content": grading_result})
    update_chat_history()

