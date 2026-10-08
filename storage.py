"""
Saves chats as plain json files in a chats/ folder so you can come back
to them later. Nothing clever, one file per conversation.
"""

import json
from datetime import datetime
from pathlib import Path

CHAT_DIR = Path("chats")


def new_id():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def save(chat_id, messages):
    if not messages:
        return
    CHAT_DIR.mkdir(exist_ok=True)
    # use the first question as the title, cut short so the sidebar stays tidy
    title = messages[0]["content"][:40]
    data = {"title": title, "messages": messages}
    (CHAT_DIR / f"{chat_id}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def load(chat_id):
    data = json.loads((CHAT_DIR / f"{chat_id}.json").read_text(encoding="utf-8"))
    return data["messages"]


def list_chats():
    """Newest first, as (id, title) pairs."""
    if not CHAT_DIR.exists():
        return []
    chats = []
    for f in sorted(CHAT_DIR.glob("*.json"), reverse=True):
        try:
            chats.append((f.stem, json.loads(f.read_text(encoding="utf-8"))["title"]))
        except (json.JSONDecodeError, KeyError):
            pass  # skip anything that got corrupted instead of crashing the app
    return chats


def delete(chat_id):
    (CHAT_DIR / f"{chat_id}.json").unlink(missing_ok=True)


def to_markdown(messages):
    """Turn a chat into a readable markdown doc, for the download button."""
    title = messages[0]["content"][:60] if messages else "empty chat"
    lines = [f"# {title}", ""]
    for msg in messages:
        who = "**You**" if msg["role"] == "user" else "**Assistant**"
        lines += [who, "", msg["content"], ""]
    return "\n".join(lines)
