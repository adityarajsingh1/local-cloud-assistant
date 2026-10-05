"""
Talking to the models. Every backend is just a function that takes the
chat history and yields the reply in small pieces (for streaming).
"""

import json
import os

import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def ollama_models():
    """Ask the local ollama server which models are pulled. Empty list if it's not running."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except requests.RequestException:
        return []


def stream_ollama(model, system, messages):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "stream": True,
    }
    with requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        # ollama sends one json object per line
        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "error" in data:
                raise RuntimeError(data["error"])
            yield data.get("message", {}).get("content", "")
            if data.get("done"):
                break


# --- cloud models ---

CLOUD_MODELS = {
    "claude": os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
}

CLOUD_KEYS = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def cloud_available():
    """Cloud providers that have an API key set."""
    return [name for name, key in CLOUD_KEYS.items() if os.getenv(key)]


def stream_claude(model, system, messages):
    import anthropic

    client = anthropic.Anthropic()
    with client.messages.stream(model=model, max_tokens=2048, system=system, messages=messages) as s:
        yield from s.text_stream


def stream_openai(model, system, messages):
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}] + messages,
        stream=True,
    )
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


STREAMERS = {
    "ollama": stream_ollama,
    "claude": stream_claude,
    "openai": stream_openai,
}


def stream(provider, model, system, messages):
    return STREAMERS[provider](model, system, messages)
