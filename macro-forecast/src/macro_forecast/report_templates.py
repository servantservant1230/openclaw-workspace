from __future__ import annotations

from datetime import datetime
from typing import Dict

from .signals import DirectionResult
from .quality import summarize_signal_quality
from .scenario import build_asset_scenarios


def _line(name: str, r: DirectionResult, q: str | None = None) -> str:
    if q:
        return f"- {name}: **{r.label}** (score={r.score:.2f}, confidence={q})"
    return f"- {name}: **{r.label}** (score={r.score:.2f})"


def build_daily_report(signals: Dict[str, DirectionResult]) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    qmap = summarize_signal_quality(signals)
    keys = ["nasdaq", "qqq", "kospi", "usdkrw", "samsung_electronics", "sk_hynix", "naver"]
    body = "\n".join(_line(k, signals[k], qmap.get(k)) for k in keys if k in signals)
    return f"# Daily Macro Direction ({ts})\n\n{body}\n"


def build_weekly_report(signals: Dict[str, DirectionResult]) -> str:
    qmap = summarize_signal_quality(signals)
    us = ["nasdaq", "qqq", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]
    kr = ["kospi", "samsung_electronics", "sk_hynix", "naver", "kr_housing_momentum"]
    us_body = "\n".join(_line(k, signals[k], qmap.get(k)) for k in us if k in signals)
    kr_body = "\n".join(_line(k, signals[k], qmap.get(k)) for k in kr if k in signals)
    return f"# Weekly Macro Outlook\n\n## US\n{us_body}\n\n## KR\n{kr_body}\n"


def build_monthly_report(signals: Dict[str, DirectionResult], features: Dict[str, float] | None = None) -> str:
    def pct(label: str) -> int:
        return {"UP": 60, "FLAT": 50, "DOWN": 40}[label]

    qmap = summarize_signal_quality(signals)
    targets = ["nasdaq", "qqq", "kospi", "samsung_electronics", "sk_hynix", "naver"]
    lines = []
    for t in targets:
        if t in signals:
            lines.append(
                f"- {t}: 방향={signals[t].label}, base_prob~{pct(signals[t].label)}%, confidence={qmap.get(t, 'LOW')}"
            )

    f = features or {}
    lines.append("\n## 핵심 지표 요약")
    lines.append(f"- us10y_change={f.get('us10y_change', 0.0):.3f}")
    lines.append(f"- dxy_change={f.get('dxy_change', 0.0):.3f}")
    lines.append(f"- fed_rate_change={f.get('fed_rate_change', 0.0):.3f}")
    lines.append(f"- memory_cycle={f.get('memory_cycle', 0.0):.3f}")
    lines.append(f"- ai_capex_momentum={f.get('ai_capex_momentum', 0.0):.3f}")

    scenario_map = build_asset_scenarios(f)
    lines.append("\n## 시나리오 (상/중/하)")
    for asset, sc in scenario_map.items():
        lines.append(f"### {asset}")
        lines.append(f"- Bull: {sc.bull}")
        lines.append(f"- Base: {sc.base}")
        lines.append(f"- Bear: {sc.bear}")

    lines.append("\n## 반증 조건")
    lines.append("- 금리/환율 급변 또는 지정학 이벤트가 발생하면 예측 신뢰도 하락")
    lines.append("- 데이터 공표 지연/개정치 반영 시 신호 재계산 필요")

    return "# Monthly Scenario Outlook\n\n" + "\n".join(lines) + "\n"
