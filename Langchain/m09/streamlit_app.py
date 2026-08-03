import uuid
import requests
import streamlit as st

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

# Each chat gets its own UUID.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Messages shown in the current Streamlit chat.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store API key during this Streamlit session.
if "api_key" not in st.session_state:
    st.session_state.api_key = ""


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def get_headers():
    return {
        "X-API-Key": st.session_state.api_key,
        "X-Session-ID": st.session_state.session_id
    }


def send_message(message: str):
    """Send user message to FastAPI /chat."""

    response = requests.post(
        f"{API_URL}/chat",
        headers=get_headers(),
        json={
            "message": message,
            "session_id": st.session_state.session_id
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()


def load_chat_history():
    """
    Load chat history from FastAPI.

    /logs/chat returns stored chats from SQLite.
    """

    response = requests.get(
        f"{API_URL}/logs/chat",
        headers=get_headers(),
        params={
            "limit": 100,
            "offset": 0
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    # Only current session
    chats = [
        chat
        for chat in data["items"]
        if chat["session_id"] == st.session_state.session_id
    ]

    # API returns newest first.
    chats.reverse()

    messages = []

    for chat in chats:
        messages.append({
            "role": "user",
            "content": chat["user_message"]
        })

        messages.append({
            "role": "assistant",
            "content": chat["ai_response"]
        })

    return messages


def new_chat():
    """Create a completely new conversation."""

    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.title("🤖 AI Assistant")

    st.text_input(
        "API Key",
        type="password",
        key="api_key"
    )

    st.divider()

    st.caption("Current Chat ID")

    st.code(
        st.session_state.session_id,
        language=None
    )

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):
        new_chat()
        st.rerun()

    if st.button(
        "🔄 Load Chat History",
        use_container_width=True
    ):

        if not st.session_state.api_key:
            st.warning("Enter your API key first.")

        else:
            try:
                st.session_state.messages = load_chat_history()
                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Could not load history: {e}")

    st.divider()

    # -----------------------------------------------------
    # API Health
    # -----------------------------------------------------

    try:

        health = requests.get(
            f"{API_URL}/health",
            timeout=3
        )

        if health.status_code == 200:
            st.success("FastAPI Connected")

        else:
            st.error("FastAPI Error")

    except requests.exceptions.RequestException:

        st.error("FastAPI Offline")


# ---------------------------------------------------------
# Main Chat UI
# ---------------------------------------------------------

st.title("AI Chat Assistant")

st.caption(
    "FastAPI + LangChain + Groq + SQLite"
)


# ---------------------------------------------------------
# Display Existing Messages
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------

prompt = st.chat_input(
    "Ask me anything..."
)


if prompt:

    # API key required by your FastAPI backend
    if not st.session_state.api_key:

        st.warning(
            "Please enter your API key in the sidebar."
        )

        st.stop()

    # -----------------------------------------------------
    # Show User Message
    # -----------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)


    # -----------------------------------------------------
    # Call FastAPI
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                result = send_message(prompt)

                answer = result["ai_response"]

                st.markdown(answer)

                # Optional information
                with st.expander("Response Details"):

                    st.write(
                        "Model:",
                        result["model_used"]
                    )

                    st.write(
                        "Duration:",
                        f'{result["duration_ms"]} ms'
                    )

                    st.write(
                        "Evaluation Score:",
                        result.get("eval_score")
                    )

                    st.write(
                        "Session ID:",
                        result["session_id"]
                    )


                # Save locally for Streamlit display
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })


            except requests.exceptions.HTTPError as e:

                if e.response.status_code == 403:

                    st.error(
                        "Invalid API key."
                    )

                else:

                    st.error(
                        f"FastAPI error: {e}"
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI. "
                    "Make sure the FastAPI server is running."
                )


            except requests.exceptions.RequestException as e:

                st.error(
                    f"Request failed: {e}"
                )