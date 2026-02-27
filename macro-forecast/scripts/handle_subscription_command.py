from __future__ import annotations

import argparse
from pathlib import Path

from macro_forecast.commands import handle_command

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "subscribers.json"


def main() -> None:
    p = argparse.ArgumentParser(description="Handle chat subscription command")
    p.add_argument("--channel", required=True, help="e.g. telegram")
    p.add_argument("--target", required=True, help="e.g. telegram user/chat id")
    p.add_argument("--text", required=True, help="incoming chat text")
    args = p.parse_args()

    result = handle_command(DB, args.channel, args.target, args.text)
    print(result.reply)


if __name__ == "__main__":
    main()
