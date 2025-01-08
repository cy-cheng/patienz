import streamlit as st
import asyncio
import pandas as pd
from model.grader import create_grader_model
import datetime
import json

GRADER_INSTRUCTION_FOLDER = "instruction_file/"
AVATAR_MAP = {"doctor": "⚕️", "patient": "😥", "grader": "🏫"}

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
    category_score = {
        "項目": "類別總分",
        "回饋": "",
        "得分": df["得分"].sum(),
        "配分": df["配分"].sum(),
    }
    df = pd.concat([df, pd.DataFrame([category_score])], ignore_index=True)
    return df, df["配分"].sum(), df["得分"].sum()

# Render table as HTML
def render_html_table(df):
    html_table = df.to_html(
        index=False,
        escape=False,
        classes="dataframe table",
        table_id="grading-results"
    )
    html_string = f"""
    <style>
        /* Table styles */
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #333333;
            padding: 8px;
            word-wrap: break-word;
            white-space: normal;
        }}
        td {{
            text-align: left;
        }}
        th {{
            background-color: var(--primary-color);
            color: var(--text-color);
            text-align: center;
        }}

        /* Theme handling */
        body {{
            color: var(--text-color);
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                --primary-color: #444444;
                --text-color: white;
            }}
        }}
        @media (prefers-color-scheme: light) {{
            body {{
                --primary-color: #e0e0e0;
                --text-color: black;
            }}
        }}
    </style>
    <div class="scrollable-table">
        {html_table}
    </div>
    """
    return html_string

# Initialize Streamlit session state
if "grading_messages" not in st.session_state:
    st.session_state.grading_messages = []
if "grade_ended" not in st.session_state:
    st.session_state.grade_ended = False

# Update chat history
def update_chat_history():
    chat_area.empty()
    with chat_area.container():
        for msg in st.session_state.grading_messages:
            with st.chat_message(msg["role"], avatar=AVATAR_MAP[msg["role"]]):
                st.markdown(msg["content"])

# Layout
st.header("評分結果")
tabs = st.tabs(["Model A", "Model B", "Model C", "Model D", "Model E"])
chat_area = st.container()

# Input form
with st.container():
    if prompt := st.chat_input("輸入您對評分的問題"):
        st.session_state.grading_messages.append({"role": "doctor", "content": prompt})
        update_chat_history()
        # Assume `grader` is initialized elsewhere
        response = st.session_state.grader.send_message(f"學生：{prompt}")
        st.session_state.grading_messages.append({"role": "grader", "content": response.text})
        update_chat_history()

subcolumns = st.columns(2)

with subcolumns[0]:
    # End grading button
    if st.button("結束評分", use_container_width=True):
        st.session_state.grade_ended = True

with subcolumns[1]:
    # Save grading data
    if st.button("儲存本次病患設定", use_container_width=True):
        data = st.session_state.data
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d')} - {data['基本資訊']['姓名']} - {data['Problem']['疾病']}.json"
        with open(f"data/problem_set/{file_name}", "w") as f:
            f.write(st.session_state.problem)

# Run grading models in parallel
if "diagnostic_ended" in st.session_state and len(st.session_state.grading_messages) == 0:
    grader_models = [create_grader_model(f"{GRADER_INSTRUCTION_FOLDER}grader_inst_{chr(65+i)}.txt") for i in range(5)]

    chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in st.session_state.diagnostic_messages])
    chat_history += f"\n特別注意：**以下是實習醫師的診斷結果：{st.session_state.diagnosis}**"
    chat_history += f"\n特別注意：**以下是實習醫師的判斷處置：{st.session_state.treatment}**"

    answer_for_grader = f"以下JSON記錄的為正確診斷與病人資訊：\n{st.session_state.data}\n"
    messages = [chat_history if i <= 2 else answer_for_grader + chat_history for i in range(5)]

    # Run models asynchronously
    async def run_models():
        tasks = [get_grading_result_async(model, msg) for model, msg in zip(grader_models, messages)]
        return await asyncio.gather(*tasks)

    grading_responses = asyncio.run(run_models())

    total_scores = 0
    gotten_scores = 0

    for i, response in enumerate(grading_responses):
        df, full_score, real_score = process_grading_result(response)
        total_scores += full_score
        gotten_scores += real_score

        with tabs[i]:
            with st.expander("評分結果", expanded=True):
                st.components.v1.html(render_html_table(df), height=400, scrolling=True)

    score_percentage = round(gotten_scores / total_scores * 100, 1)
    st.write(f"得分率：{score_percentage}%")


