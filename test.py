"""
Install an additional SDK for JSON schema support Google AI Python SDK

$ pip install google.ai.generativelanguage
"""

import os
import google.generativeai as genai
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
    properties = {
      "response": content.Schema(
        type = content.Type.STRING,
      ),
      "score": content.Schema(
        type = content.Type.INTEGER,
      ),
      "float": content.Schema(
        type = content.Type.NUMBER,
      ),
      "Obj": content.Schema(
        type = content.Type.OBJECT,
        properties = {
          "intInObj": content.Schema(
            type = content.Type.INTEGER,
          ),
          "strInObj": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "Here's a blurb for an upcoming startup event. Rewrite this in a more professional tone intended for a corporate email. \n\n\"Calling all tech junkies, investors, and curious minds! 🤖🧠🎉\n\nReady to witness the future? We're throwing a pitch party where brilliant startups will showcase their mind-blowing AI creations. Think healthcare that reads your mind (almost!), businesses that run themselves (we wish!), and robots that make you coffee (we definitely need!).Whether you're an investor, a budding entrepreneur, or just someone who wants to geek out over AI, this event is your jam! Come watch the pitches, mingle with industry experts, and get inspired by these rockstar companies. Oh, and did we mention free food and drinks? Register now before the robots take all the spots! 😉\"",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Subject: Invitation:  AI Innovation Showcase & Networking Event\n\nDear [Name],\n\nWe cordially invite you to an exclusive showcase of cutting-edge AI innovations, featuring promising startups poised to disrupt key industries.  This event offers a unique opportunity to network with industry leaders, explore groundbreaking technologies, and learn about investment prospects in the rapidly evolving AI landscape.\n\nAttendees will witness compelling pitches from startups developing AI-driven solutions across diverse sectors, including advancements in healthcare, automation, and other innovative applications.  The event will provide ample opportunities for networking and discussion with entrepreneurs and industry experts.\n\nRefreshments will be served.\n\nWe encourage you to register your attendance at [Registration Link] at your earliest convenience, as space is limited.\n\nWe look forward to welcoming you.\n\n\nSincerely,\n\nThe [Your Organization Name] Team\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "tell me a joke and give me a score\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```json\n",
        "{\"response\": \"Why don't scientists trust atoms? Because they make up everything!\", \"score\": 8.5}",
        "\n```",
      ],
    },
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)
