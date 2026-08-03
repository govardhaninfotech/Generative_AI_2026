import streamlit as st

from api import send_message

st.set_page_config(page_title="Simple AI Chat")

st.title("🤖 Simple AI Chat")

question = st.text_input("Ask Anything")

if st.button("Send"):

    if question:

        with st.spinner("Thinking..."):

            answer = send_message(question)

        st.success("AI Response")

        st.write(answer)
