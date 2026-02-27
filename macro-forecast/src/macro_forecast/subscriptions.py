from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


@dataclass
class Subscriber:
    channel: str
    target: str
    cadence: str  # daily|weekly|monthly|all
    active: bool = True


class SubscriptionStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> List[Subscriber]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [Subscriber(**x) for x in payload.get("subscribers", [])]

    def save(self, subs: List[Subscriber]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"subscribers": [asdict(s) for s in subs]}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def subscribe(self, channel: str, target: str, cadence: str = "all") -> None:
        subs = self.load()
        for s in subs:
            if s.channel == channel and s.target == target:
                s.cadence = cadence
                s.active = True
                self.save(subs)
                return
        subs.append(Subscriber(channel=channel, target=target, cadence=cadence, active=True))
        self.save(subs)

    def unsubscribe(self, channel: str, target: str) -> bool:
        subs = self.load()
        changed = False
        for s in subs:
            if s.channel == channel and s.target == target and s.active:
                s.active = False
                changed = True
        if changed:
            self.save(subs)
        return changed

    def for_cadence(self, cadence: str) -> List[Subscriber]:
        out = []
        for s in self.load():
            if not s.active:
                continue
            if s.cadence in ("all", cadence):
                out.append(s)
        return out
