from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .commands import handle_command


@dataclass
class WebhookAction:
    chat_id: Optional[str]
    reply_text: Optional[str]


def extract_message(update: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    msg = update.get("message") or update.get("edited_message") or {}
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = msg.get("text")
    if chat_id is None or not text:
        return None, None
    return str(chat_id), str(text)


def process_update(db_path: Path, update: Dict[str, Any], channel: str = "telegram") -> WebhookAction:
    chat_id, text = extract_message(update)
    if not chat_id or not text:
        return WebhookAction(chat_id=None, reply_text=None)

    if not text.strip().startswith("/"):
        return WebhookAction(chat_id=chat_id, reply_text=None)

    result = handle_command(db_path=db_path, channel=channel, target=chat_id, text=text)
    return WebhookAction(chat_id=chat_id, reply_text=result.reply)
