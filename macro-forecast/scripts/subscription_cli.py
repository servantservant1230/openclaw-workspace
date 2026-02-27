from __future__ import annotations

import argparse
from pathlib import Path

from macro_forecast.subscriptions import SubscriptionStore

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "subscribers.json"


def main() -> None:
    p = argparse.ArgumentParser(description="subscription management")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--channel", required=True)
    p_add.add_argument("--target", required=True)
    p_add.add_argument("--cadence", default="all", choices=["daily", "weekly", "monthly", "all"])

    p_del = sub.add_parser("remove")
    p_del.add_argument("--channel", required=True)
    p_del.add_argument("--target", required=True)

    sub.add_parser("list")

    args = p.parse_args()
    store = SubscriptionStore(DB)

    if args.cmd == "add":
        store.subscribe(args.channel, args.target, args.cadence)
        print("subscribed")
    elif args.cmd == "remove":
        ok = store.unsubscribe(args.channel, args.target)
        print("unsubscribed" if ok else "not_found")
    elif args.cmd == "list":
        for s in store.load():
            print(f"{s.channel}:{s.target} cadence={s.cadence} active={s.active}")


if __name__ == "__main__":
    main()
