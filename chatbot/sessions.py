import streamlit as st


def initialize_session():
    """Initialize Streamlit session state."""

    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if "chat_title" not in st.session_state:
        st.session_state.chat_title = "New Conversation"

    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None