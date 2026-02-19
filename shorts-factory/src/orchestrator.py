from pathlib import Path
from datetime import datetime
import json

BASE = Path(__file__).resolve().parents[1]


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def research_agent():
    # TODO: RSS/YouTube 메타 수집 구현
    return {
        "selected_topic": "미국 금리 동결과 원화 변동성",
        "keywords": ["금리", "환율", "물가", "연준"],
        "news_summary": [
            {"fact": "연준이 기준금리를 동결했다", "source_type": "news"},
            {"fact": "원/달러 환율 변동성이 확대됐다", "source_type": "news"}
        ],
        "confidence": "medium"
    }


def planner(research):
    return {
        "hook": "이번 주 금융시장에서 가장 중요한 신호 하나만 짚겠습니다.",
        "core": [
            "금리 동결이 시장 심리에 미친 영향",
            "환율 변동성과 개인에게 미치는 체감 포인트"
        ],
        "cta": "내 상황에서는 어떤 리스크가 큰지 먼저 점검해보세요."
    }


def script_agent(plan, research):
    return {
        "draft_script": """[Hook]\n이번 주 금융시장에서 중요한 신호 하나만 보겠습니다.\n\n[Core]\n연준의 금리 동결 이후, 시장은 안도와 경계를 동시에 반영하고 있습니다.\n특히 환율 변동성이 커지면 체감 물가와 해외결제 부담에 영향이 갈 수 있습니다.\n핵심은 숫자 하나보다, 내 지출 구조가 환율 변화에 얼마나 민감한지 점검하는 것입니다.\n\n[CTA]\n지금은 수익 기대보다 리스크 관리 기준부터 세워보세요."""
    }


def deep_verifier(draft):
    # TODO: Codex 검증 API 연동
    return {
        "issues": [],
        "risk_level": "Low",
        "fixed_script": draft["draft_script"],
        "rationale": "현재 문안에서 확정적 투자 권유 문구가 없음"
    }


def legal_risk_agent(script_text: str):
    disclaimer = "※ 본 내용은 일반적인 정보이며 개인 상황에 따라 다를 수 있습니다."
    return {
        "risk_level": "Low",
        "final_script": script_text + "\n\n" + disclaimer
    }


def subtitle_agent(script_text: str):
    # TODO: 2~3초 분할 고도화
    lines = [l.strip() for l in script_text.splitlines() if l.strip()]
    blocks = []
    t = 0
    for idx, line in enumerate(lines, start=1):
        start = f"00:00:{t:02d},000"
        t2 = t + 3
        end = f"00:00:{t2:02d},000"
        blocks.append(f"{idx}\n{start} --> {end}\n{line}\n")
        t = t2
    return "\n".join(blocks)


def main():
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    research = research_agent()
    save_json(BASE / "research" / "latest.json", research)

    plan = planner(research)
    save_json(BASE / "metadata" / "plan.json", plan)

    draft = script_agent(plan, research)
    (BASE / "outputs" / "script_draft.md").write_text(draft["draft_script"])

    verified = deep_verifier(draft)
    save_json(BASE / "metadata" / "verification.json", verified)

    if verified["risk_level"] == "High":
        save_json(BASE / "logs" / f"run-{run_id}.json", {"status": "stopped", "reason": "risk_high"})
        return

    legal = legal_risk_agent(verified["fixed_script"])
    save_json(BASE / "metadata" / "legal_risk.json", legal)

    (BASE / "outputs" / "script_final.md").write_text(legal["final_script"])
    srt = subtitle_agent(legal["final_script"])
    (BASE / "subtitles" / "latest.srt").write_text(srt)

    save_json(BASE / "logs" / f"run-{run_id}.json", {
        "status": "completed",
        "risk_level": legal["risk_level"],
        "artifacts": [
            "research/latest.json",
            "metadata/plan.json",
            "metadata/verification.json",
            "metadata/legal_risk.json",
            "outputs/script_final.md",
            "subtitles/latest.srt"
        ]
    })


if __name__ == "__main__":
    main()
