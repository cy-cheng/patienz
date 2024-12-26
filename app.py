import streamlit as st
from model.problem_setter import create_problem_setter_model
from model.patient import create_patient_model
from model.grader import create_grader_model
import setup.sidebar
import json

# Configure instruction file paths
PROBLEM_SETTER_INSTRUCTION = "instruction_file/problem_setter_instruction.txt"
PATIENT_INSTRUCTION = "instruction_file/patient_instruction.txt"
GRADER_INSTRUCTION = "instruction_file/grader_inst_gpt.txt"


# Initialize models in session state
if "problem_setter_model" not in st.session_state:
    problem_setter_model = create_problem_setter_model(PROBLEM_SETTER_INSTRUCTION)
    st.session_state.problem_setter_model = problem_setter_model
    st.session_state.problem_setter = st.session_state.problem_setter_model.start_chat()

if "patient_model" not in st.session_state and "problem" in st.session_state:
    patient_model = create_patient_model(PATIENT_INSTRUCTION, st.session_state.problem)
    st.session_state.patient_model = patient_model
    st.session_state.patient = st.session_state.patient_model.start_chat()

# sidebar 
setup.sidebar.patient_info()
setup.sidebar.note()

if "user_config" in st.session_state and "problem" not in st.session_state:
    config = "\n".join([f"{key}: {value}" for key, value in st.session_state.user_config.items()])
    st.write(f"User Config:\n{config}")
    st.session_state.problem = st.session_state.problem_setter.send_message("請利用以下資訊幫我出題：\n" + config).text

    print(st.session_state.problem)

# Create output message block

st.header("對話區")
output_container = st.container(height=400)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun

chat_history_output = output_container.empty()

# Define avatar map 
avatar_map = {
    "doctor": "🧑‍⚕️",
    "patient": "😥",
    "grader": "🧑‍🏫"
}

def move_focus():
    # inspect the html to determine which control to specify to receive focus (e.g. text or textarea).
    st.components.v1.html(
        f"""
            <script>
                var textarea = window.parent.document.querySelectorAll("textarea[type=textarea]");
                for (var i = 0; i < textarea.length; ++i) {{
                    textarea[i].focus();
                }}
            </script>
        """,
    )

def update_chat_history():
    with chat_history_output.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=avatar_map[message["role"]]):
                st.markdown(message["content"])

        move_focus()


update_chat_history()

# Accept user input
input_container = st.container()
with input_container:
    if prompt := st.chat_input("Enter Something", key="user_input"):
        # Prepare the chat history for the model
        chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]

        # Add user message to chat history
        st.session_state.messages.append({"role": "doctor", "content": prompt})
        update_chat_history()
        
        # Check if the diagnostic session has ended
        if "diagnostic_ended" in st.session_state and st.session_state.diagnostic_ended:
            # Send the user input to the grader model
            grader_response = st.session_state.grader.send_message(f"醫學生：{prompt}")
            # Add grader response to chat history
            st.session_state.messages.append({"role": "grader", "content": grader_response.text})
        else:
            # Send the chat history to the patient model
            response = st.session_state.patient.send_message(f"醫生：{prompt}")

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "patient", "content": response.text})

        update_chat_history()

# Add a confirm answer button outside the input container
button_container = st.container()
with button_container:
    if st.button("完成問診"):
        # Initialize the grader model and chat
        if "grader_model" not in st.session_state:
            grader_model = create_grader_model(GRADER_INSTRUCTION)
            st.session_state.grader_model = grader_model
            st.session_state.grader = st.session_state.grader_model.start_chat()
        
        # Prepare the chat history for the grader model
        chat_history = "\n".join([f"{msg['role']}：{msg['content']}" for msg in st.session_state.messages])
        
        # Send the chat history to the grader model
        grader_response = st.session_state.grader.send_message("以下是問診記錄：\n"+chat_history)

        print(grader_response.text)

        # Convert grader_response.text to JSON
        # grader_response_json = json.loads(grader_response.text)
        # print(grader_response_json)

        # Display grader response in chat message container with different profile picture color
        with st.chat_message("grader"):
            st.markdown(grader_response.text)
        # Add grader response to chat history
        st.session_state.messages.append({"role": "grader", "content": grader_response.text})
        
        # Mark the diagnostic session as ended
        st.session_state.diagnostic_ended = True

