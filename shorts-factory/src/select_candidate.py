from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]


def score_item(item):
    risk = item.get("verification", {}).get("risk_level", "Medium")
    risk_score = {"Low": 3, "Medium": 1, "High": -5}.get(risk, 0)

    topic = item.get("topic", "")
    topic_bonus = 1 if any(k in topic for k in ["환율", "금리", "증시"]) else 0

    script_path = BASE / item.get("script_file", "")
    length_bonus = 0
    if script_path.exists():
        txt = script_path.read_text()
        n = len(txt)
        if 280 <= n <= 700:
            length_bonus = 2

    return risk_score + topic_bonus + length_bonus


def main():
    bundle = json.loads((BASE / "outputs" / "bundle.json").read_text())
    items = bundle.get("items", [])
    if not items:
        raise SystemExit("No bundle items")

    ranked = []
    for it in items:
        s = score_item(it)
        it2 = dict(it)
        it2["score"] = s
        ranked.append(it2)

    ranked.sort(key=lambda x: x["score"], reverse=True)
    selected = ranked[0]

    out = {
        "run_id": bundle.get("run_id"),
        "selected": selected,
        "candidates": ranked,
    }
    (BASE / "outputs" / "selection.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
