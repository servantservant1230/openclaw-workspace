from __future__ import annotations

import csv
from pathlib import Path

from macro_forecast.sensitivity import stock_weight_maps, top_feature_sensitivity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample_features.csv"
OUT = ROOT / "outputs"


def load_latest_features(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
    return {k: float(v) for k, v in row.items()}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    feats = load_latest_features(DATA)

    lines = ["# Stock Sensitivity Snapshot", ""]
    for stock, wm in stock_weight_maps().items():
        lines.append(f"## {stock}")
        for feat, c in top_feature_sensitivity(feats, wm, top_n=4):
            lines.append(f"- {feat}: contribution={c:.3f}")
        lines.append("")

    out = OUT / "stock_sensitivity.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("generated:", out)


if __name__ == "__main__":
    main()
