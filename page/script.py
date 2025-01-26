import asyncio
import sys
from model.grader import create_grader_model
import streamlit as st 

ss = st.session_state
INSTRUCTION_FOLDER = "instruction_file/"

async def get_grading_result_async(current_model, messages_for_grading):
    grader = current_model.start_chat()
    response = await grader.send_message_async(messages_for_grading)
    return response.text

def main():
    grader_models = [create_grader_model(f"{INSTRUCTION_FOLDER}grader_inst_{chr(65+i)}.txt") for i in range(5)]

    chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in ss.diagnostic_messages])
    chat_history += f"\n特別注意：**以下是實習醫師的診斷結果：{ss.diagnosis}**"
    chat_history += f"\n特別注意：**以下是實習醫師的判斷處置：{ss.treatment}**"

    answer_for_grader = f"以下JSON記錄的為正確診斷與病人資訊：\n{ss.data}\n"
    messages = [chat_history if i <= 2 else answer_for_grader + chat_history for i in range(5)]

    async def run_models():
        tasks = [get_grading_result_async(model, msg) for model, msg in zip(grader_models, messages)]
        return await asyncio.gather(*tasks)

    ss.grading_results = asyncio.run(run_models())
    
if __name__ == "__main__":
    main()
    
