import streamlit as st
import asyncio
import pandas as pd
from model.grader import create_grader_model
from model.advisor import create_advisor_model
import page.dialog as dialog
import datetime
import json

INSTRUCTION_FOLDER = "instruction_file/"
AVATAR_MAP = {"student": "⚕️", "patient": "😥", "advisor": "🏫"}

# Async helper for running grading models in parallel
async def get_grading_result_async(current_model, messages_for_grading):
    grader = current_model.start_chat()
    response = await grader.send_message_async(messages_for_grading)
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
if "advice_messages" not in st.session_state:
    st.session_state.advice_messages = []
if "grade_ended" not in st.session_state:
    st.session_state.grade_ended = False

# Layout
st.header("評分結果")
tabs = st.tabs(["病況詢問", "病史詢問", "溝通技巧與感情支持", "鑑別診斷", "疾病處置"])


# Run grading models in parallel
if "diagnostic_ended" in st.session_state and "advisor" not in st.session_state:
    grader_models = [create_grader_model(f"{INSTRUCTION_FOLDER}grader_inst_{chr(65+i)}.txt") for i in range(5)]

    chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in st.session_state.diagnostic_messages])
    chat_history += f"\n特別注意：**以下是實習醫師的診斷結果：{st.session_state.diagnosis}**"
    chat_history += f"\n特別注意：**以下是實習醫師的判斷處置：{st.session_state.treatment}**"

    answer_for_grader = f"以下JSON記錄的為正確診斷與病人資訊：\n{st.session_state.data}\n"
    messages = [chat_history if i <= 2 else answer_for_grader + chat_history for i in range(5)]

    # Run models asynchronously
    async def run_models():
        tasks = [get_grading_result_async(model, msg) for model, msg in zip(grader_models, messages)]
        return await asyncio.gather(*tasks)

    with st.spinner("評分中..."):
        st.session_state.grading_responses = asyncio.run(run_models())


    total_scores = 0
    gotten_scores = 0

    for i, response in enumerate(st.session_state.grading_responses):
        df, full_score, real_score = process_grading_result(response)
        total_scores += full_score
        gotten_scores += real_score

    st.session_state.score_percentage = round(gotten_scores / total_scores * 100, 1)
    st.session_state.advice_messages = [{"role": "advisor", "content": f"你的得分率是：{st.session_state.score_percentage}%"}]

    create_advisor_model(f"{INSTRUCTION_FOLDER}advisor_instruction.txt")

if "advisor" in st.session_state:
    for i, response in enumerate(st.session_state.grading_responses):
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
    chat_area.empty()
    with chat_area.container(height=350):
        for msg in st.session_state.advice_messages:
            print(msg)
            with st.chat_message(msg["role"], avatar=AVATAR_MAP[msg["role"]]):
                st.markdown(msg["content"])


update_chat_history()

# Input form
if prompt := st.chat_input("輸入您對評分的問題"):
    st.session_state.advice_messages.append({"role": "student", "content": prompt})
    update_chat_history()

    response = st.session_state.advisor.send_message(f"學生：{prompt}")
    st.session_state.advice_messages.append({"role": "advisor", "content": response.text})
    update_chat_history()

subcolumns = st.columns(2)

with subcolumns[0]:
    # End grading button
    if st.button("結束評分", use_container_width=True):
        st.session_state.grade_ended = True
        dialog.refresh()

with subcolumns[1]:
    # Save grading data
    if st.button("儲存本次病患設定", use_container_width=True):
        data = st.session_state.data
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d')} - {data['基本資訊']['姓名']} - {data['Problem']['疾病']} - {st.session_state.score_percentage}%.json"
        with open(f"data/problem_set/{file_name}", "w") as f:
            f.write(st.session_state.problem)

        dialog.config_saved(file_name)
