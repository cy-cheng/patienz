import time
import os
import google.generativeai as genai

# Configure the Gemini API

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Set up the model generation configuration
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Helper functions
def upload_to_gemini(path, mime_type=None):
    """Uploads a PDF to the Gemini API."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for uploaded files to become active for processing."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready\n")

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Upload a PDF
pdf_path = "./ay2024-2025.pdf"  # Replace with your PDF file path
files = [
    upload_to_gemini(pdf_path, mime_type="application/pdf"),
]

# Wait for the files to be ready
wait_for_files_active(files)

# Start a chat session with the uploaded PDF
chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                files[0],
                "You will try and answer questions on the content of the input PDF files.\n\n",
            ],
        },
    ]
)

# Example queries
questions = [
    "What is the Instructional Period for Semester 2? List out all the weeks.",
]

# Process the questions and print responses
for question in questions:
    print(f"asking: {question}")
    response = chat_session.send_message(question)
    print(f"Question: {question}\nAnswer: {response.text}\n")

