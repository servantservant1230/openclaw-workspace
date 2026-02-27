from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ScenarioTriplet:
    bull: str
    base: str
    bear: str


def build_asset_scenarios(features: Dict[str, float]) -> Dict[str, ScenarioTriplet]:
    """간단한 규칙 기반 시나리오 생성.

    - bull: 금리/달러 하락 + 성장 모멘텀 개선
    - bear: 금리/달러 상승 + 경기둔화
    """
    ai = features.get("ai_capex_momentum", 0.0)
    mem = features.get("memory_cycle", 0.0)
    dxy = features.get("dxy_change", 0.0)
    y10 = features.get("us10y_change", 0.0)

    us_base = "금리·달러 안정, AI 투자 모멘텀 유지"
    us_bull = "미10년물/달러 하락 + AI Capex 확대 시 밸류에이션 리레이팅"
    us_bear = "미10년물/달러 재상승 + 물가 상방 시 성장주 멀티플 압축"

    kr_base = "원화 변동성 완화, 수출 모멘텀 보합"
    kr_bull = "메모리 업사이클 강화 + 수출 개선 시 반도체 주도 랠리"
    kr_bear = "환율 급등 + 대외수요 둔화 시 주도주 변동성 확대"

    if ai < 0:
        us_base = "AI 투자 둔화 신호, 선택적 종목장"
    if mem < 0:
        kr_base = "메모리 사이클 둔화, 실적 추정치 하향 압력"
    if dxy > 0.05 or y10 > 0.05:
        us_bear = "달러·금리 동반 강세 시 기술주 조정 리스크 확대"

    return {
        "us_equity": ScenarioTriplet(bull=us_bull, base=us_base, bear=us_bear),
        "kr_equity": ScenarioTriplet(bull=kr_bull, base=kr_base, bear=kr_bear),
    }
