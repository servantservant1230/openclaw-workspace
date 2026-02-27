from __future__ import annotations

from typing import Dict, List, Tuple


def top_feature_sensitivity(base: Dict[str, float], mapping: Dict[str, float], top_n: int = 5) -> List[Tuple[str, float]]:
    """단순 선형 가중치 기반 민감도 근사.

    반환: 절대 기여도 기준 상위 (feature, contribution)
    """
    contribs = []
    for feat, w in mapping.items():
        v = float(base.get(feat, 0.0))
        contribs.append((feat, w * v))
    contribs.sort(key=lambda x: abs(x[1]), reverse=True)
    return contribs[:top_n]


def stock_weight_maps() -> Dict[str, Dict[str, float]]:
    return {
        "samsung_electronics": {
            "memory_cycle": 0.20,
            "ai_capex_momentum": 0.10,
            "usdkrw_change": -0.20,
            "us10y_change": -0.20,
        },
        "sk_hynix": {
            "memory_cycle": 0.30,
            "ai_capex_momentum": 0.12,
            "usdkrw_change": -0.20,
            "us10y_change": -0.20,
        },
        "naver": {
            "ad_market_momentum": 0.08,
            "us10y_change": -0.10,
            "dxy_change": -0.15,
        },
        "NVDA": {
            "ai_capex_momentum": 0.18,
            "memory_cycle": 0.12,
            "us10y_change": -0.25,
        },
    }
