from __future__ import annotations

import csv
import io
import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class MarketSnapshot:
    asof: str
    values: Dict[str, float]


FRED_SERIES = {
    "us_cpi_yoy": "CPIAUCSL",
    "us_unemployment_rate": "UNRATE",
    "fed_funds_rate": "FEDFUNDS",
    "us10y_yield": "DGS10",
    "dxy": "DTWEXBGS",
    "brent_usd": "DCOILBRENTEU",
}


def _http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "macro-forecast-mvp/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def fetch_fred_latest(series_id: str, api_key: Optional[str] = None) -> Optional[float]:
    if not api_key:
        return None
    q = urllib.parse.urlencode(
        {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 1,
        }
    )
    url = f"https://api.stlouisfed.org/fred/series/observations?{q}"
    try:
        raw = _http_get(url)
        data = json.loads(raw)
        obs = data.get("observations", [])
        if not obs:
            return None
        v = obs[0].get("value")
        if v in (None, "."):
            return None
        return float(v)
    except Exception:
        return None


def fetch_stooq_latest(symbol: str) -> Optional[float]:
    url = f"https://stooq.com/q/l/?s={urllib.parse.quote(symbol.lower())}&f=sd2t2ohlcv&h&e=csv"
    try:
        raw = _http_get(url)
        reader = csv.DictReader(io.StringIO(raw))
        row = next(reader, None)
        if not row:
            return None
        close = row.get("Close")
        if not close or close == "N/D":
            return None
        return float(close)
    except Exception:
        return None


def build_snapshot() -> MarketSnapshot:
    fred_key = os.environ.get("FRED_API_KEY")
    values: Dict[str, float] = {}

    # FRED series (optional key)
    for k, sid in FRED_SERIES.items():
        v = fetch_fred_latest(sid, fred_key)
        if v is not None:
            values[k] = v

    # price proxies via stooq (no key)
    price_map = {
        "nasdaq_close": "^ixic.us",
        "qqq_close": "qqq.us",
        "kospi_close": "^kospi",
        "AAPL_close": "aapl.us",
        "MSFT_close": "msft.us",
        "NVDA_close": "nvda.us",
        "AMZN_close": "amzn.us",
        "GOOGL_close": "googl.us",
        "META_close": "meta.us",
        "TSLA_close": "tsla.us",
        "samsung_electronics_close": "005930.kr",
        "sk_hynix_close": "000660.kr",
        "naver_close": "035420.kr",
    }
    for k, sym in price_map.items():
        v = fetch_stooq_latest(sym)
        if v is not None:
            values[k] = v

    return MarketSnapshot(asof=datetime.utcnow().strftime("%Y-%m-%d"), values=values)
