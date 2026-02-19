from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[1]


def main():
    sel = json.loads((BASE / "outputs" / "selection.json").read_text())
    s = sel["selected"]
    topic = s.get("topic", "금융 이슈")
    script_file = BASE / s.get("script_file")
    script_text = script_file.read_text() if script_file.exists() else ""

    description_disclaimer = s.get("disclaimer", {}).get(
        "description", "※ 본 내용은 일반적인 정보이며 개인 상황에 따라 다를 수 있습니다."
    )

    titles = [
        f"{topic} 오늘 핵심 30초 정리",
        f"{topic} 지금 꼭 볼 포인트",
        f"{topic} 한 번에 이해하기"
    ]

    hashtags = [
        "#금융", "#재테크", "#경제", "#환율", "#금리", "#증시", "#뉴스요약", "#쇼츠", "#투자", "#시장분석"
    ]

    package = {
        "topic": topic,
        "script_file": s.get("script_file"),
        "srt_file": s.get("srt_file"),
        "titles": titles,
        "description": "\n".join([
            f"[{topic}] 오늘 핵심 요약입니다.",
            "",
            script_text[:500],
            "",
            description_disclaimer,
            "",
            " ".join(hashtags)
        ]),
        "hashtags": hashtags,
        "thumbnail_text_options": [
            f"{topic} 핵심 30초",
            f"지금 봐야 할 {topic}"
        ]
    }

    out = BASE / "outputs" / "publish_package.json"
    out.write_text(json.dumps(package, ensure_ascii=False, indent=2))
    print(json.dumps(package, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
