from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .subscriptions import SubscriptionStore


@dataclass
class CommandResult:
    ok: bool
    reply: str


def handle_command(db_path: Path, channel: str, target: str, text: str) -> CommandResult:
    store = SubscriptionStore(db_path)
    raw = (text or "").strip()
    if not raw:
        return CommandResult(False, "명령이 비어 있습니다.")

    tokens = raw.split()
    cmd = tokens[0].lower()

    if cmd in {"/start", "start"}:
        return CommandResult(
            True,
            (
                "안녕하세요, 경제읽어주는개발자입니다.\n"
                "구독 명령: /subscribe daily|weekly|monthly|all\n"
                "해지 명령: /unsubscribe\n"
                "상태 확인: /status"
            ),
        )

    if cmd in {"/subscribe", "subscribe"}:
        cadence = "all"
        if len(tokens) >= 2:
            cadence = tokens[1].lower()
        if cadence not in {"daily", "weekly", "monthly", "all"}:
            return CommandResult(False, "cadence는 daily|weekly|monthly|all 중 하나여야 합니다.")
        store.subscribe(channel=channel, target=target, cadence=cadence)
        return CommandResult(True, f"구독 완료: cadence={cadence}")

    if cmd in {"/unsubscribe", "unsubscribe"}:
        ok = store.unsubscribe(channel=channel, target=target)
        if ok:
            return CommandResult(True, "구독 해지 완료")
        return CommandResult(False, "활성 구독이 없습니다.")

    if cmd in {"/status", "status"}:
        subs = [s for s in store.load() if s.channel == channel and s.target == target and s.active]
        if not subs:
            return CommandResult(True, "현재 구독 없음")
        return CommandResult(True, f"현재 구독: {subs[0].cadence}")

    return CommandResult(False, "지원하지 않는 명령입니다. /start 로 도움말을 확인하세요.")
