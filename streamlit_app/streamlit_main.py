import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app", "modules"))

from main_agent import chatbot_turn

opening_message = "Hi, thanks for applying to our Python Developer role. Could you share a bit about your Python experience?"

st.title("SMS Recruiting Bot")
st.subheader("Python Developer Position - Proof of Concept")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": opening_message}]

if "ended" not in st.session_state:
    st.session_state.ended = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.ended:
    st.info("The conversation has ended. Refresh the page to start a new one.")
else:
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        history = ""
        for msg in st.session_state.messages[:-1]:
            if msg["role"] == "assistant":
                history = history + "recruiter: " + msg["content"] + "\n"
            else:
                history = history + "candidate: " + msg["content"] + "\n"

        with st.spinner("Thinking..."):
            action, reply = chatbot_turn(history, user_input)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        if action == "end":
            st.session_state.ended = True
            st.info("The conversation has ended. Refresh the page to start a new one.")
