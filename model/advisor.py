import os
import google.generativeai as genai
import streamlit as st

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def create_advisor_model(advisor_instruction_path: str, problem: str):
    with open(advisor_instruction_path, 'r', encoding='utf-8') as file:
        advisor_instruction = file.read()

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    st.session_state.patient_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=f"{advisor_instruction}",
    )

    st.session_state.patient = st.session_state.patient_model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    [],
                    genai.upload_file("tmp/symptom.pdf", mime_type="application/pdf"),
                    genai.upload_file("tmp/diagnosis.pdf", mime_type="application/pdf"),
                ]
            }
        ],
    )

