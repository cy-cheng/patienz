import os
import google.generativeai as genai
from util.search import search_and_export_to_pdf
import streamlit as st

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def create_patient_model(patient_instruction_path: str, problem: str):
    with open(patient_instruction_path, 'r', encoding='utf-8') as file:
        patient_instruction = file.read()

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
        system_instruction=f"{patient_instruction}{problem}",
    )

    keyword = st.session_state.data["Problem"]["疾病"]
    search_and_export_to_pdf(f"{keyword} 症狀", "tmp/symptom.pdf")

    st.session_state.patient = st.session_state.patient_model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                   genai.upload_file("tmp/symptom.pdf", mime_type="application/pdf"),
                   "請參照這份文件回答以下的問診。"
                ]
            }
        ],
    )
    
