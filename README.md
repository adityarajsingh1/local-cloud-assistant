# local-cloud-assistant 🏠☁️

A small chat app where you can switch between a **local model** running on your own machine (through [Ollama](https://ollama.com)) and **cloud models** (Claude and GPT), even in the middle of a conversation.

I built this because I wanted to use local models for everyday stuff (free, private, works offline) and only reach for the big cloud models when a question actually needs them. Having both in one window makes that really easy. It's built with Streamlit, so it's a proper web UI but still just a few Python files.

## Features

- chat UI in the browser, answers stream in as they're written
- pick any model you've pulled in Ollama, or Claude / GPT if you have API keys
- switch models mid-chat. The new model sees the whole conversation so far
- editable system prompt in the sidebar
- chats are saved automatically and listed in the sidebar so you can reopen or delete them
- export any chat as a markdown file with one click
- works with only local models, only cloud models, or both

## Setup

Python 3.9+.

```bash
git clone https://github.com/adityarajsingh1/local-cloud-assistant.git
cd local-cloud-assistant
python -m venv .venv
source .venv/bin/activate      # windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**For local models**, install Ollama and pull a model:

```bash
ollama pull llama3.2
ollama serve        # if it isn't already running in the background
```

**For cloud models** (optional), set the keys you have:

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
```

## Run it

```bash
streamlit run app.py
```

It opens at http://localhost:8501. Choose a model in the sidebar and start chatting.

## How it's put together

- `app.py` is the Streamlit UI: sidebar, chat window, and saving after each reply
- `backends.py` has one streaming function per provider (Ollama over its HTTP API, Claude and OpenAI through their SDKs). They all take the same arguments, so the app doesn't care which one it's talking to
- `storage.py` saves each conversation as a JSON file in `chats/`

## What I want to add next

- [ ] "auto" mode that sends easy questions to the local model and hard ones to the cloud
- [ ] show response time and token count under each answer
- [x] export a chat as markdown
- [ ] upload a file and chat about it
- [ ] Gemini support
