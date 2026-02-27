from __future__ import annotations

from typing import Dict


DEFAULTS = {
    "us_cpi_yoy_change": 0.0,
    "us_unemployment_change": 0.0,
    "fed_rate_change": 0.0,
    "us10y_change": 0.0,
    "dxy_change": 0.0,
    "brent_change": 0.0,
    "usdkrw_change": 0.0,
    "kr_cpi_change": 0.0,
    "bok_rate_change": 0.0,
    "ai_capex_momentum": 0.2,
    "memory_cycle": 0.2,
    "consumption_momentum": 0.1,
    "ad_market_momentum": 0.1,
    "export_momentum": 0.1,
    "real_income_momentum": 0.1,
}


def derive_features_from_levels(current: Dict[str, float], previous: Dict[str, float]) -> Dict[str, float]:
    def pct(k: str, fallback: float = 0.0) -> float:
        c = current.get(k)
        p = previous.get(k)
        if c is None or p in (None, 0):
            return fallback
        return (c - p) / abs(p)

    out = dict(DEFAULTS)
    out["us_cpi_yoy_change"] = pct("us_cpi_yoy")
    out["us_unemployment_change"] = pct("us_unemployment_rate")
    out["fed_rate_change"] = pct("fed_funds_rate")
    out["us10y_change"] = pct("us10y_yield")
    out["dxy_change"] = pct("dxy")
    out["brent_change"] = pct("brent_usd")
    return out
