"""
Professor Bot — Memory System
Stores conversation history per user in JSON files
"""
import json
import os
from datetime import datetime
from pathlib import Path
from config import MEMORY_DIR, MAX_HISTORY_PER_USER


def _user_path(user_id: int) -> Path:
    return MEMORY_DIR / f"{user_id}.json"


def get_history(user_id: int) -> list:
    """Get conversation history for a user."""
    path = _user_path(user_id)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(user_id: int, history: list):
    """Save conversation history for a user."""
    path = _user_path(user_id)
    if len(history) > MAX_HISTORY_PER_USER:
        history = history[-MAX_HISTORY_PER_USER:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_message(user_id: int, role: str, content: str):
    """Add a message to user's history and save."""
    history = get_history(user_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    save_history(user_id, history)


def clear_history(user_id: int):
    """Clear all history for a user."""
    path = _user_path(user_id)
    if path.exists():
        os.remove(path)


def format_for_openai(history: list) -> list:
    """Convert stored history to OpenAI-format messages (only role/content)."""
    messages = []
    for msg in history:
        if msg["role"] in ("user", "assistant", "system"):
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    return messages


def get_stats(user_id: int) -> dict:
    """Get memory stats for a user."""
    history = get_history(user_id)
    user_msgs = sum(1 for m in history if m["role"] == "user")
    bot_msgs = sum(1 for m in history if m["role"] == "assistant")
    return {
        "total_messages": len(history),
        "user_messages": user_msgs,
        "bot_messages": bot_msgs,
        "first_seen": history[0]["timestamp"] if history else None,
        "last_seen": history[-1]["timestamp"] if history else None,
    }
