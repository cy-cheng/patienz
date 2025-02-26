import os
import google.generativeai as genai
import streamlit as st

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

ss = st.session_state

def create_advisor_model(advisor_instruction_path: str):
    with open(advisor_instruction_path, 'r', encoding='utf-8') as file:
        advisor_instruction = file.read()

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    ss.advisor_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=f"{advisor_instruction}",
    )

    ss.advisor = ss.advisor_model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [res for res in ss.grading_responses] + [genai.upload_file("tmp/symptom.pdf", mime_type="application/pdf"), "\n".join([f"{msg['role']}：{msg['content']}" for msg in ss.diagnostic_messages])],
            }
        ],
    )

