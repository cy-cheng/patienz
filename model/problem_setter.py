"""
Install an additional SDK for JSON schema support Google AI Python SDK

$ pip install google.ai.generativelanguage
"""

import os
import google.generativeai as genai
import streamlit as st
from google.ai.generativelanguage_v1beta.types import content

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = [],
    required = ["基本資訊", "MH", "FH", "SH", "Problem"],
    properties = {
      "基本資訊": content.Schema(
        type = content.Type.OBJECT,
        enum = [],
        required = ["姓名", "年齡", "身高", "體重", "性別", "職業", "生日"],
        properties = {
          "姓名": content.Schema(
            type = content.Type.STRING,
          ),
          "年齡": content.Schema(
            type = content.Type.INTEGER,
          ),
          "身高": content.Schema(
            type = content.Type.INTEGER,
          ),
          "體重": content.Schema(
            type = content.Type.NUMBER,
          ),
          "性別": content.Schema(
            type = content.Type.STRING,
          ),
          "生日": content.Schema(
            type = content.Type.STRING,
          ),
          "職業": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
      "MH": content.Schema(
        type = content.Type.OBJECT,
        enum = [],
        required = ["既往疾病", "過敏史", "藥物史", "目前病史"],
        properties = {
          "既往疾病": content.Schema(
            type = content.Type.STRING,
          ),
          "目前病史": content.Schema(
            type = content.Type.STRING,
          ),
          "過敏史": content.Schema(
            type = content.Type.STRING,
          ),
          "藥物史": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
      "FH": content.Schema(
        type = content.Type.OBJECT,
        enum = [],
        required = ["直系血親疾病"],
        properties = {
          "直系血親疾病": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
      "SH": content.Schema(
        type = content.Type.OBJECT,
        enum = [],
        required = ["生活習慣", "飲食", "菸酒", "旅遊史"],
        properties = {
          "生活習慣": content.Schema(
            type = content.Type.STRING,
          ),
          "飲食": content.Schema(
            type = content.Type.STRING,
          ),
          "菸酒": content.Schema(
            type = content.Type.STRING,
          ),
          "旅遊史": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
      "Problem": content.Schema(
        type = content.Type.OBJECT,
        enum = [],
        required = ["疾病", "排除可能疾病之診斷", "確認正確疾病之診斷", "處置方式"],
        properties = {
          "疾病": content.Schema(
            type = content.Type.STRING,
          ),
          "排除可能疾病之診斷": content.Schema(
            type = content.Type.STRING,
          ),
          "確認正確疾病之診斷": content.Schema(
            type = content.Type.STRING,
          ),
          "處置方式": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
    },
  ),
  "response_mime_type": "application/json",
}


def create_problem_setter_model(problem_instruction_path: str):
    with open(problem_instruction_path, 'r', encoding='utf-8') as file:
        problem_setter_instruction = file.read()

    st.session_state.problem_setter_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=problem_setter_instruction,
    )

    st.session_state.problem_setter = st.session_state.problem_setter_model.start_chat()

