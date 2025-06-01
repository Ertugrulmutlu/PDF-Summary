import streamlit as st
from datetime import datetime

def init_session_state():
    """Initialize Streamlit session state."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def add_message(role, content):
    """Add a new message to chat history."""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })