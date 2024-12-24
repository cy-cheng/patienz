import streamlit as st
from models.problem_setter import create_problem_setter_model
from models.patient import create_patient_model
from models.grader import create_grader_model

# Configure instruction file paths
PROBLEM_SETTER_INSTRUCTION = "instruction_files/problem_setter_instruction.txt"
PATIENT_INSTRUCTION = "instruction_files/patient_instruction.txt"
GRADER_INSTRUCTION = "instruction_files/grader_instruction.txt"

# Initialize models in session state
if "problem_setter_model" not in st.session_state:
    problem_setter_model = create_problem_setter_model(PROBLEM_SETTER_INSTRUCTION)
    st.session_state.problem_setter_model = problem_setter_model
    st.session_state.problem_setter = st.session_state.problem_setter_model.start_chat()
    st.session_state.problem = (st.session_state.problem_setter.send_message("請開始出題")).text

    print(st.session_state.problem)

if "patient_model" not in st.session_state:
    patient_model = create_patient_model(PATIENT_INSTRUCTION, st.session_state.problem)
    st.session_state.patient_model = patient_model
    st.session_state.patient = st.session_state.patient_model.start_chat()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
input_container = st.container()
with input_container:
    if prompt := st.chat_input("Enter Something", key="user_input"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare the chat history for the model
        chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        
        # Check if the diagnostic session has ended
        if "diagnostic_ended" in st.session_state and st.session_state.diagnostic_ended:
            # Send the user input to the grader model
            grader_response = st.session_state.grader.send_message(f"醫學生：{prompt}")
            # Display grader response in chat message container with different profile picture color
            with st.chat_message("grader"):
                st.markdown(grader_response.text)
            # Add grader response to chat history
            st.session_state.messages.append({"role": "grader", "content": grader_response.text})
        else:
            # Send the chat history to the patient model
            response = st.session_state.patient.send_message(f"醫生：{prompt}")
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response.text)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response.text})

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
        grader_response = st.session_state.grader.send_message(chat_history)

        # print(grader_response.text)
        
        # Display grader response in chat message container with different profile picture color
        with st.chat_message("grader"):
            st.markdown(grader_response.text)
        # Add grader response to chat history
        st.session_state.messages.append({"role": "grader", "content": grader_response.text})
        
        # Mark the diagnostic session as ended
        st.session_state.diagnostic_ended = True


