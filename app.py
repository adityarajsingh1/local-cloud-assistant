"""
A little chat app where you can switch between a local model (Ollama)
and cloud models (Claude, OpenAI) in the middle of a conversation.
Run it with:  streamlit run app.py
"""

import streamlit as st

import backends
import storage

st.set_page_config(page_title="local + cloud assistant", page_icon="🤖")
st.title("🤖 local + cloud assistant")


# streamlit reruns the whole script on every interaction,
# so the chat history has to live in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_id = storage.new_id()

with st.sidebar:
    local_models = backends.ollama_models()
    cloud = backends.cloud_available()

    # build one list of choices like "ollama · llama3.2" or "claude · claude-sonnet-5-5"
    options = [("ollama", m) for m in local_models]
    options += [(name, backends.CLOUD_MODELS[name]) for name in cloud]

    if not options:
        st.error("No models found. Start Ollama (`ollama serve`) or set an API key.")
        st.stop()

    provider, model = st.selectbox("model", options, format_func=lambda o: f"{o[0]} · {o[1]}")
    st.caption("🏠 runs on your machine" if provider == "ollama" else "☁️ cloud model")
    if not local_models:
        st.caption("(Ollama isn't running, so only cloud models are listed)")

    system = st.text_area("system prompt", "You are a friendly, helpful assistant.")
    if st.button("➕ new chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_id = storage.new_id()
        st.rerun()

    st.subheader("past chats")
    for chat_id, title in storage.list_chats():
        col1, col2 = st.columns([5, 1])
        if col1.button(title, key=f"open-{chat_id}", use_container_width=True):
            st.session_state.messages = storage.load(chat_id)
            st.session_state.chat_id = chat_id
            st.rerun()
        if col2.button("🗑", key=f"del-{chat_id}"):
            storage.delete(chat_id)
            if chat_id == st.session_state.chat_id:
                st.session_state.messages = []
                st.session_state.chat_id = storage.new_id()
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
            reply = st.write_stream(backends.stream(provider, model, system, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": reply})
            storage.save(st.session_state.chat_id, st.session_state.messages)
        except Exception as e:
            st.error(f"something went wrong: {e}")
            st.session_state.messages.pop()
