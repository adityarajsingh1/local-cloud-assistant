"""
A little chat app that runs on a local model through Ollama.
Run it with:  streamlit run app.py
"""

import streamlit as st

import backends

st.set_page_config(page_title="local + cloud assistant", page_icon="🤖")
st.title("🤖 local + cloud assistant")

SYSTEM = "You are a friendly, helpful assistant."

# streamlit reruns the whole script on every interaction,
# so the chat history has to live in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    models = backends.ollama_models()
    if not models:
        st.error("Can't reach Ollama. Is it running? (`ollama serve`)")
        st.stop()
    model = st.selectbox("model", models)
    if st.button("new chat"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("ask me something"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(backends.stream_ollama(model, SYSTEM, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"something went wrong: {e}")
            st.session_state.messages.pop()
