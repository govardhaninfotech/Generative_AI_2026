import streamlit as st

from api import send_message

st.set_page_config(page_title="AI ChatBot", layout="wide")

st.title("🤖 AI ChatBot")


if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


prompt = st.chat_input("Type your message...")


if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):

        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = send_message(prompt)

            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
