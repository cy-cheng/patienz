from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import pandas as pd
from model.grader import create_grader_model
from model.advisor import create_advisor_model
import util.dialog as dialog
import datetime
import json

INSTRUCTION_FOLDER = "instruction_file/"
AVATAR_MAP = {"student": "⚕️", "patient": "😥", "advisor": "🏫"}

ss = st.session_state


# Helper function to run grading models
def get_grading_result_sync(current_model, messages_for_grading):
    grader = current_model.start_chat()
    response = grader.send_message(messages_for_grading)
    return response.text


# Process grading results into a DataFrame
def process_grading_result(input_json):
    grading_result = json.loads(input_json)
    sorted_result = sorted(grading_result, key=lambda x: x['id'])

    rows = []
    for data in sorted_result:
        rows.append({
            "項目": data['item'],
            "回饋": data['feedback'],
            "得分": int(data['real_score']),
            "配分": int(data['full_score']),
        })

    df = pd.DataFrame(rows)
    return df, df["配分"].sum(), df["得分"].sum()


def render_html_table(df):
    left_align = lambda x: f"<div style='text-align: left;'>{x}</div>"
    cent_align = lambda x: f"<div style='text-align: center;'>{x}</div>"

    html_table = df.to_html(
        index=False,
        escape=False,
        classes="dataframe table",
        table_id="grading-results",
        col_space="4em",
        formatters=[left_align, left_align, cent_align, cent_align],
        justify="center",
    )

    return html_table


# Initialize Streamlit session state
if "advice_messages" not in ss:
    ss.advice_messages = []
if "grade_ended" not in ss:
    ss.grade_ended = False

# Layout
st.header("評分結果")
tabs = st.tabs(["病況詢問", "病史詢問", "溝通技巧與感情支持", "鑑別診斷", "疾病處置"])

# Run grading models in parallel using ThreadPoolExecutor
if "diagnostic_ended" in ss and "advisor" not in ss:
    grader_models = [create_grader_model(f"{INSTRUCTION_FOLDER}grader_inst_{chr(65+i)}.txt") for i in range(5)]
    chat_history = f"***醫學生與病人的對話紀錄如下：***\n"
    chat_history += "\n".join([f"{msg['role']}：{msg['content']}" for msg in ss.diagnostic_messages])
    chat_history += f"\n特別注意：**以下是實習醫師的診斷結果：{ss.diagnosis}**"
    chat_history += f"\n特別注意：**以下是實習醫師的鑑別診斷：{ss.ddx}**"
    chat_history += f"\n特別注意：**以下是實習醫師的判斷處置：{ss.treatment}**"
    chat_history += f"***醫學生與病人的對話紀錄結束***\n"

    answer_for_grader = f"以下JSON記錄的為正確診斷與病人資訊：\n{ss.data}\n"
    messages = [chat_history if i <= 2 else answer_for_grader + chat_history for i in range(5)]

    def run_models_sync():
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [executor.submit(get_grading_result_sync, model, msg) for model, msg in zip(grader_models, messages)]
            return [task.result() for task in tasks]

    with st.spinner("評分中..."):
        ss.grading_responses = run_models_sync()

    total_scores = 0
    gotten_scores = 0

    for i, response in enumerate(ss.grading_responses):
        df, full_score, real_score = process_grading_result(response)
        total_scores += full_score
        gotten_scores += real_score

    ss.score_percentage = round(gotten_scores / total_scores * 100, 1)
    ss.advice_messages = [{"role": "advisor", "content": f"你的得分率是：{ss.score_percentage}%"}]

    create_advisor_model(f"{INSTRUCTION_FOLDER}advisor_instruction.txt")

if "advisor" in ss:
    for i, response in enumerate(ss.grading_responses):
        df, full_score, real_score = process_grading_result(response)

        with tabs[i]:
            st.subheader(f"細項評分")
            with st.expander(f"本領域獲得分數：（{real_score}/{full_score}）", expanded=True):
                with st.container(height=350):
                    st.markdown(render_html_table(df), unsafe_allow_html=True)

st.subheader("建議詢問")

output_container = st.container()
chat_area = output_container.empty()


# Update chat history
def update_chat_history():
    with chat_area.container(height=350):
        for msg in ss.advice_messages:
            with st.chat_message(msg["role"], avatar=AVATAR_MAP[msg["role"]]):
                st.markdown(msg["content"])


update_chat_history()

# Input form
if prompt := st.chat_input("輸入您對評分的問題"):
    ss.advice_messages.append({"role": "student", "content": prompt})
    update_chat_history()

    response = ss.advisor.send_message(f"學生：{prompt}")
    ss.advice_messages.append({"role": "advisor", "content": response.text})
    update_chat_history()

subcolumns = st.columns(2)

with subcolumns[0]:
    # End grading button
    if st.button("結束評分", use_container_width=True):
        ss.grade_ended = True
        dialog.refresh()

with subcolumns[1]:
    # Save grading data
    if st.button("儲存本次病患設定", use_container_width=True):
        data = ss.data
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d')} - {data['基本資訊']['姓名']} - {data['Problem']['疾病']} - {ss.score_percentage}%.json"
        with open(f"data/problem_set/{file_name}", "w") as f:
            f.write(ss.problem)

        dialog.config_saved(file_name)
