from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .subscriptions import SubscriptionStore


@dataclass
class CommandResult:
    ok: bool
    reply: str


def _help_text() -> str:
    return (
        "안녕하세요, 경제읽어주는개발자입니다.\n"
        "도움말: /help\n"
        "구독: /subscribe daily|weekly|monthly|all\n"
        "해지: /unsubscribe\n"
        "상태: /status\n"
        "오늘 리포트 즉시보기: /today [daily|weekly|monthly]"
    )


def _read_report(db_path: Path, cadence: str) -> str:
    report = db_path.parent.parent / "outputs" / f"{cadence}.md"
    if not report.exists():
        return f"{cadence} 리포트가 아직 생성되지 않았습니다."
    text = report.read_text(encoding="utf-8")
    if len(text) > 3500:
        return text[:3500] + "\n\n...(메시지 길이 제한으로 일부 생략)"
    return text


def handle_command(db_path: Path, channel: str, target: str, text: str) -> CommandResult:
    store = SubscriptionStore(db_path)
    raw = (text or "").strip()
    if not raw:
        return CommandResult(False, "명령이 비어 있습니다.")

    tokens = raw.split()
    cmd = tokens[0].lower()

    if cmd in {"/start", "start", "/help", "help"}:
        return CommandResult(True, _help_text())

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

    if cmd in {"/today", "today"}:
        cadence = "daily"
        if len(tokens) >= 2:
            cadence = tokens[1].lower()
        if cadence not in {"daily", "weekly", "monthly"}:
            return CommandResult(False, "today 옵션은 daily|weekly|monthly 중 하나여야 합니다.")
        return CommandResult(True, _read_report(db_path, cadence))

    return CommandResult(False, "지원하지 않는 명령입니다. /help 로 도움말을 확인하세요.")
