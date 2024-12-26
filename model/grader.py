import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def create_grader_model(grader_instruction_path: str):
    with open(grader_instruction_path, 'r', encoding='utf-8') as file:
        grader_instruction = file.read()

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    """
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_schema": content.Schema(
            type=content.Type.ARRAY,
            items=content.Schema( 
                type=content.Type.OBJECT,
                properties={
                    "item": content.Schema(type=content.Type.STRING),
                    "full_score": content.Schema(type=content.Type.INTEGER),
                    "real_score": content.Schema(type=content.Type.INTEGER),
                    "feedback": content.Schema(type=content.Type.STRING),
                },
            )
        ),
        "response_mime_type": "application/json",
    }
    """

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=grader_instruction,
    )
    return model

