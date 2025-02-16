import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from util.tools import getPDF
import streamlit as st

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

ss = st.session_state

def create_value_examiner_model(examiner_instruction_path: str, problem: str):
    with st.spinner("正在搜尋病症資料..."):
        keyword = st.session_state.data["Problem"]["englishDiseaseName"]
        getPDF(f"{keyword} uptodate clinical features", f"tmp/{ss.sid}_features.pdf")

    with st.spinner("正在建立檢查模型..."): 
        with open(examiner_instruction_path, 'r', encoding='utf-8') as file:
            examiner_instruction = file.read()

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_schema": content.Schema(
                type = content.Type.OBJECT,
                properties = {
                    "value_type_item": content.Schema(
                        type = content.Type.ARRAY,
                        items = content.Schema(
                            type = content.Type.OBJECT,
                            properties = {
                                "englishName": content.Schema(type=content.Type.STRING),
                                "value": content.Schema(type=content.Type.STRING),
                            },
                        ),
                    ),
                },
            ), 
            "response_mime_type": "application/json",
        }

        ss.examiner_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=f"{examiner_instruction}{problem}",
        )

        ss.examiner = ss.examiner_model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                       genai.upload_file(f"tmp/{ss.sid}_features.pdf", mime_type="application/pdf"),
                       "please refer to this document to generate the examination report for the following: "
                    ]
                }
            ],
        )
    

def create_text_examiner_model(examiner_instruction_path: str, problem: str):
    with st.spinner("正在搜尋病症資料..."):
        keyword = st.session_state.data["Problem"]["englishDiseaseName"]
        getPDF(f"{keyword} uptodate clinical features", f"tmp/{ss.sid}_features.pdf")

    with st.spinner("正在建立檢查模型..."): 
        with open(examiner_instruction_path, 'r', encoding='utf-8') as file:
            examiner_instruction = file.read()

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        ss.examiner_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=f"{examiner_instruction}{problem}",
        )

        ss.examiner = ss.examiner_model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                       genai.upload_file(f"tmp/{ss.sid}_features.pdf", mime_type="application/pdf"),
                       "please refer to this document to generate the examination report for the following: "
                    ]
                }
            ],
        )
    
