import streamlit as st 
import util.constants as const

ss = st.session_state

def update(chat_area, msgs, height, show_all=False):
    chat_area.empty()
    with chat_area.container(height=height):
        if show_all:
            for msg in msgs:
                with st.chat_message(msg["role"], avatar=const.avatar_map[msg["role"]]):
                    st.markdown(msg["content"])
        else:
            for msg in msgs[-2:]:
                try:
                    with st.chat_message(msg["role"], avatar=const.avatar_map[msg["role"]]):
                        st.markdown(msg["content"])
                except:
                    pass

def append(msgs, role, content):
    msgs.append({"role": role, "content": content})
