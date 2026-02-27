from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class DirectionResult:
    score: float
    label: str  # UP | FLAT | DOWN


def _to_label(score: float, up: float = 0.25, down: float = -0.25) -> str:
    if score >= up:
        return "UP"
    if score <= down:
        return "DOWN"
    return "FLAT"


def build_signal_map(features: Dict[str, float]) -> Dict[str, DirectionResult]:
    """Rule-based MVP scoring.

    features 예시 키:
    us_cpi_yoy_change, us_unemployment_change, fed_rate_change, us10y_change,
    dxy_change, brent_change, usdkrw_change, kr_cpi_change, bok_rate_change,
    ai_capex_momentum, memory_cycle
    """
    f = lambda k, d=0.0: float(features.get(k, d))

    # 공통 매크로 압력 (금리/달러/유가 상승은 성장주에 역풍 가정)
    macro_risk_off = (
        0.30 * f("fed_rate_change")
        + 0.25 * f("us10y_change")
        + 0.20 * f("dxy_change")
        + 0.15 * f("brent_change")
        + 0.10 * f("us_cpi_yoy_change")
    )

    # 미국 지수
    nasdaq_score = -macro_risk_off - 0.15 * f("us_unemployment_change")
    qqq_score = nasdaq_score + 0.05 * f("ai_capex_momentum")

    # 미 기술주 바스켓 (기본 동일 + 종목 민감도)
    tech_base = qqq_score
    us_tech = {
        "AAPL": tech_base - 0.03 * f("dxy_change"),
        "MSFT": tech_base + 0.05 * f("ai_capex_momentum"),
        "NVDA": tech_base + 0.18 * f("ai_capex_momentum") + 0.12 * f("memory_cycle"),
        "AMZN": tech_base + 0.03 * f("consumption_momentum"),
        "GOOGL": tech_base + 0.02 * f("ad_market_momentum"),
        "META": tech_base + 0.02 * f("ad_market_momentum"),
        "TSLA": tech_base - 0.08 * f("us10y_change") - 0.05 * f("brent_change"),
    }

    # 한국 시장
    kospi_score = (
        -0.20 * f("usdkrw_change")
        -0.20 * f("us10y_change")
        -0.15 * f("dxy_change")
        -0.10 * f("brent_change")
        +0.20 * f("memory_cycle")
        +0.15 * f("export_momentum")
    )

    kr_housing_score = (
        -0.35 * f("bok_rate_change")
        -0.25 * f("usdkrw_change")
        -0.15 * f("kr_cpi_change")
        +0.20 * f("real_income_momentum")
    )

    kr_leaders = {
        "samsung_electronics": kospi_score + 0.20 * f("memory_cycle") + 0.10 * f("ai_capex_momentum"),
        "sk_hynix": kospi_score + 0.30 * f("memory_cycle") + 0.12 * f("ai_capex_momentum"),
        "naver": kospi_score - 0.10 * f("us10y_change") + 0.08 * f("ad_market_momentum"),
    }

    result: Dict[str, DirectionResult] = {
        "nasdaq": DirectionResult(nasdaq_score, _to_label(nasdaq_score)),
        "qqq": DirectionResult(qqq_score, _to_label(qqq_score)),
        "kospi": DirectionResult(kospi_score, _to_label(kospi_score)),
        "usdkrw": DirectionResult(f("usdkrw_change"), _to_label(f("usdkrw_change"), up=0.15, down=-0.15)),
        "kr_housing_momentum": DirectionResult(kr_housing_score, _to_label(kr_housing_score)),
    }

    for k, v in us_tech.items():
        result[k] = DirectionResult(v, _to_label(v))
    for k, v in kr_leaders.items():
        result[k] = DirectionResult(v, _to_label(v))

    return result
