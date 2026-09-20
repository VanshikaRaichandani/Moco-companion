import streamlit as st

# -----------------------------
# 1. Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Moco AI",
    page_icon="🌿",
    layout="centered"
)

from chatbot.prompts import SYSTEM_PROMPT
from chatbot.llm import generate_response
from chatbot.database import (
    create_tables,
    create_conversation,
    get_conversations,
    save_message,
    load_messages,
    delete_conversation,
    update_conversation_title
)
from chatbot.sessions import initialize_session


# -----------------------------
# 2. Database & Session Setup
# -----------------------------
create_tables()
initialize_session()

# Create a conversation if none exists
if st.session_state.current_conversation_id is None:
    conversation_id = create_conversation()
    st.session_state.current_conversation_id = conversation_id


# -----------------------------
# 3. Constants
# -----------------------------
INITIAL_GREETING = "Hi! 👋 I'm Moco. How are you feeling today?"


# -----------------------------
# 4. Initialize Chat History
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:

    db_messages = load_messages(
        st.session_state.current_conversation_id
    )

    if db_messages:
        st.session_state.messages = db_messages

    else:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": INITIAL_GREETING
            }
        ]

        save_message(
            st.session_state.current_conversation_id,
            "assistant",
            INITIAL_GREETING
        )


# -----------------------------
# 5. Sidebar
# -----------------------------
with st.sidebar:

    st.title("🌿 Moco AI")
    st.caption(
        "Your AI companion for reflection and emotional support."
    )

    st.divider()

    # -----------------------------
    # New Chat
    # -----------------------------
    if st.button(
        "➕ New Chat",
        use_container_width=True,
        key="new_chat_button"
    ):

        # Create a completely new conversation
        conversation_id = create_conversation()

        st.session_state.current_conversation_id = conversation_id

        # Reset messages
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": INITIAL_GREETING
            }
        ]

        # Save greeting to new conversation
        save_message(
            st.session_state.current_conversation_id,
            "assistant",
            INITIAL_GREETING
        )

        st.session_state.chat_title = "New Conversation"
        st.session_state.confirm_delete = False

        st.rerun()

    st.divider()

    # -----------------------------
    # Saved Conversations
    # -----------------------------
    st.markdown("### 💬 Your Chats")

    conversations = get_conversations()

    if conversations:

        for conversation in conversations:

            conversation_id = conversation[0]
            conversation_title = conversation[1]

            if st.button(
                conversation_title,
                use_container_width=True,
                key=f"conversation_{conversation_id}"
            ):

                # Switch to selected conversation
                st.session_state.current_conversation_id = (
                    conversation_id
                )

                # Load its messages
                st.session_state.messages = load_messages(
                    conversation_id
                )

                # Set current title
                st.session_state.chat_title = conversation_title

                st.session_state.confirm_delete = False

                st.rerun()

    else:
        st.caption("No saved conversations yet.")

    st.divider()

    # -----------------------------
    # Current Chat
    # -----------------------------
    st.markdown("### 💬 Current Chat")

    title = st.session_state.get(
        "chat_title",
        "New Conversation"
    )

    st.info(title)

    st.divider()

    # -----------------------------
    # Clear Current Chat
    # -----------------------------
    if st.button(
        "🗑 Clear Current Chat",
        use_container_width=True,
        key="clear_current_chat_button"
    ):
        st.session_state.confirm_delete = True

    if st.session_state.get(
        "confirm_delete",
        False
    ):

        st.warning(
            "Delete this conversation permanently?"
        )

        col1, col2 = st.columns(2)

        # Delete / clear
        with col1:

            if st.button(
                "Delete",
                use_container_width=True,
                type="primary",
                key="confirm_delete_button"
            ):

                delete_conversation(
                    st.session_state.current_conversation_id
                )

                # Put greeting back
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": INITIAL_GREETING
                    }
                ]

                save_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    INITIAL_GREETING
                )

                st.session_state.chat_title = "New Conversation"
                st.session_state.confirm_delete = False

                st.rerun()

        # Cancel
        with col2:

            if st.button(
                "Cancel",
                use_container_width=True,
                key="cancel_delete_button"
            ):
                st.session_state.confirm_delete = False
                st.rerun()

    st.divider()

    st.caption("⚙️ Settings (Coming Soon)")


# -----------------------------
# 6. Main UI
# -----------------------------
st.title("🌿 Moco AI")

st.caption(
    "Your AI companion for reflection and emotional support."
)

st.info(
    "⚠️ Moco is an AI companion, not a licensed therapist "
    "or medical professional."
)


# -----------------------------
# 7. Render Messages
# -----------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# 8. User Input
# -----------------------------
user_input = st.chat_input(
    "Type your message..."
)


if user_input:

    # -----------------------------
    # Update Chat Title
    # -----------------------------
    if st.session_state.chat_title == "New Conversation":
        title = user_input.strip()

        if len(title) > 35:
            title = title[:35] + "..."

        st.session_state.chat_title = title

        update_conversation_title(
            st.session_state.current_conversation_id,
            title
    )


    # -----------------------------
    # Save User Message
    # -----------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    save_message(
        st.session_state.current_conversation_id,
        "user",
        user_input
    )


    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)


    # -----------------------------
    # Generate Moco Response
    # -----------------------------
    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""

        for chunk in generate_response(
            st.session_state.messages,
            SYSTEM_PROMPT
        ):

            full_response += chunk

            placeholder.markdown(
                full_response + "▌"
            )

        placeholder.markdown(
            full_response
        )


    # -----------------------------
    # Save Moco Response
    # -----------------------------
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )

    save_message(
        st.session_state.current_conversation_id,
        "assistant",
        full_response
    )

    st.rerun()