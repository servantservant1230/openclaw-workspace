from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]

NEWS_RSS = [
    # Korean finance sources (priority)
    "https://www.hankyung.com/feed/finance",
    "https://www.mk.co.kr/rss/40300001/",
    "https://rss.edaily.co.kr/stock_news.xml",
    "https://www.fnnews.com/rss/fn_realnews_all.xml",
    # KR-filtered Google News finance stream
    "https://news.google.com/rss/search?q=%EA%B8%88%EB%A6%AC+OR+%ED%99%98%EC%9C%A8+OR+%EC%A6%9D%EC%8B%9C+when:1d&hl=ko&gl=KR&ceid=KR:ko",
    # Global backfill (fallback)
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",
]

YOUTUBE_SIGNAL_FEEDS = [
    # stable channel feeds (title/desc signal only)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCIALMKvObZNtJ6AmdCLP7Lg",  # Bloomberg TV
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvJJ_dzjViJCoLf5uKUTwoA",  # CNBC
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCEAZeUIeJs0IjQiqTCdVSIg",  # Yahoo Finance
]

KOR_STOPWORDS = {
    "그리고", "하지만", "대한", "관련", "이슈", "시장", "오늘", "최근", "기자", "뉴스",
    "대한민국", "에서", "으로", "까지", "했다", "한다", "있다", "없다",
    "with", "the", "this", "that", "from", "into", "about", "video", "breaking", "news", "update",
    "and", "for", "are", "was", "were", "will", "its", "their", "has", "have", "had",
    "after", "before", "amid", "over", "under", "than", "into", "out", "how", "why",
    "what", "when", "where", "which", "your", "you", "his", "her", "our", "they",
    "stock", "stocks", "market", "markets", "finance", "financial", "money", "today",
    "live", "podcast", "episode", "watch", "shows", "show", "new", "latest"
}

DISCLAIMER = "※ 본 내용은 일반적인 정보이며 개인 상황에 따라 다를 수 있습니다."


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def fetch_xml(url: str, timeout: int = 12):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return ET.fromstring(raw)


def clean_text(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_rss_items(root, limit=12):
    items = []
    for it in root.findall(".//item")[:limit]:
        title = clean_text(it.findtext("title", ""))
        desc = clean_text(it.findtext("description", ""))
        link = clean_text(it.findtext("link", ""))
        pub_date = clean_text(it.findtext("pubDate", ""))
        if title:
            items.append({
                "title": title,
                "description": desc,
                "link": link,
                "pub_date": pub_date,
                "source_type": "news"
            })
    return items


def parse_atom_entries(root, limit=12):
    ns = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/"}
    entries = []
    for en in root.findall("a:entry", ns)[:limit]:
        title = clean_text(en.findtext("a:title", "", ns))
        desc = clean_text(en.findtext("m:group/m:description", "", ns))
        published = clean_text(en.findtext("a:published", "", ns))
        link_node = en.find("a:link", ns)
        link = link_node.attrib.get("href", "") if link_node is not None else ""
        if title:
            entries.append({
                "title": title,
                "description": desc,
                "link": link,
                "published": published,
                "source_type": "youtube_signal"
            })
    return entries


def tokenize(text: str):
    text = re.sub(r"https?://\S+", " ", text.lower())
    text = re.sub(r"[^0-9A-Za-z가-힣 ]", " ", text)
    toks = [t for t in text.split() if len(t) >= 2 and t not in KOR_STOPWORDS and not t.isdigit()]
    return toks


def extract_keywords(news_items, yt_items, topk=15):
    # Korean news 중심으로 가중치 부여, 유튜브는 트렌드 신호로만 약하게 반영
    c = Counter()
    for row in news_items:
        toks = tokenize(f"{row.get('title','')}")
        c.update(toks)
        c.update(toks)  # news x2 weight

    for row in yt_items:
        c.update(tokenize(f"{row.get('title','')}"))

    blacklist = {
        "to", "on", "of", "in", "is", "as", "at", "by", "an", "be", "it", "or", "if", "more",
        "follow", "bloomberg", "cnbc", "youtube", "channel", "official", "watch",
        "https", "http", "www", "com", "nbsp", "connect", "facebook"
    }

    finance_priority = [
        # Korean first
        "금리", "환율", "달러", "원화", "물가", "인플레", "증시", "코스피", "코스닥", "국채", "채권", "연준",
        # English fallback
        "fed", "rate", "rates", "interest", "fomc", "inflation", "cpi", "dollar", "fx", "currency",
        "treasury", "bond", "yield", "stocks", "equity", "gold", "bitcoin", "oil", "earnings"
    ]

    ranked = [k for k, _ in c.most_common(160) if k not in blacklist]

    prioritized = []
    for p in finance_priority:
        for k in ranked:
            if p in k and k not in prioritized:
                prioritized.append(k)

    for k in ranked:
        if k not in prioritized:
            prioritized.append(k)

    return prioritized[:topk]


def topic_priority_map():
    return [
        ("금리/연준(Fed)", ["금리", "연준", "fomc", "fed", "rate", "rates", "interest"]),
        ("환율/달러", ["환율", "달러", "원화", "dollar", "fx", "currency", "yen", "won"]),
        ("인플레이션/물가", ["물가", "인플레", "inflation", "prices", "cpi"]),
        ("증시 변동성", ["증시", "코스피", "코스닥", "stocks", "equity", "nasdaq", "s&p", "dow"]),
        ("채권/국채", ["국채", "채권", "treasury", "bond", "yields", "yield"]),
        ("원자재/에너지", ["유가", "금값", "원자재", "oil", "gold", "commodity"]),
    ]


def select_topics(keywords, news_items, max_topics=3):
    joined_titles = " ".join([n.get("title", "") for n in news_items]).lower()
    topics = []
    for topic_name, needles in topic_priority_map():
        if any(n in joined_titles for n in needles):
            topics.append(f"{topic_name} 관련 최신 금융 이슈")
        if len(topics) >= max_topics:
            break

    if not topics:
        for k in keywords:
            if k not in {"https", "http", "www", "com", "to", "on", "of", "in", "is"}:
                topics.append(f"{k} 관련 최신 금융 이슈")
                break

    if not topics:
        topics = ["거시경제 변동성 이슈"]

    return topics




def topic_needles_map():
    return {
        "금리/연준(Fed) 관련 최신 금융 이슈": ["금리", "연준", "fomc", "fed", "rate", "rates", "interest"],
        "환율/달러 관련 최신 금융 이슈": ["환율", "달러", "원화", "dollar", "fx", "currency", "yen", "won"],
        "인플레이션/물가 관련 최신 금융 이슈": ["물가", "인플레", "inflation", "prices", "cpi"],
        "증시 변동성 관련 최신 금융 이슈": ["증시", "코스피", "코스닥", "주가", "stocks", "equity", "nasdaq", "s&p", "dow"],
        "채권/국채 관련 최신 금융 이슈": ["국채", "채권", "treasury", "bond", "yields", "yield"],
        "원자재/에너지 관련 최신 금융 이슈": ["유가", "금값", "원자재", "oil", "gold", "commodity"],
    }


def classify_topic_for_title(title: str, topics):
    title_l = title.lower()
    best_topic = topics[0] if topics else "거시경제 변동성 이슈"
    best_score = -1
    needles_map = topic_needles_map()
    for t in topics:
        needles = needles_map.get(t, [])
        score = sum(1 for n in needles if n in title_l)
        if score > best_score:
            best_score = score
            best_topic = t
    return best_topic, best_score


def summarize_news_facts(news_items, topics, limit_per_topic=4, total_limit=12):
    out = []
    seen = set()
    topic_count = {t: 0 for t in topics}

    # 전 기사에 대해 주제 분류 점수 산정
    scored_all = []
    for n in news_items:
        topic_guess, score = classify_topic_for_title(n.get("title", ""), topics)
        scored_all.append((score, topic_guess, n))

    # 점수 높은 순으로 배치, 토픽별 cap 유지
    scored_all.sort(key=lambda x: x[0], reverse=True)
    for score, topic_guess, n in scored_all:
        if len(out) >= total_limit:
            break
        if topic_count.get(topic_guess, 0) >= limit_per_topic:
            continue
        key = n.get("link") or n.get("title")
        if key in seen:
            continue
        if any(jaccard_tokens(n.get("title", ""), ex.get("fact", "")) >= 0.62 for ex in out):
            continue

        # 무관 기사 배제: score 0은 후순위
        if score <= 0 and len(out) < max(6, len(topics) * 2):
            continue

        out.append({
            "topic": topic_guess,
            "fact": n["title"],
            "source_type": "news",
            "source": n.get("link", "")
        })
        seen.add(key)
        topic_count[topic_guess] = topic_count.get(topic_guess, 0) + 1

    # 부족하면 아직 cap 여유가 있는 토픽에만 보충
    if len(out) < total_limit:
        for _, topic_guess, n in scored_all:
            if len(out) >= total_limit:
                break
            if topic_count.get(topic_guess, 0) >= limit_per_topic:
                continue
            key = n.get("link") or n.get("title")
            if key in seen:
                continue
            if any(jaccard_tokens(n.get("title", ""), ex.get("fact", "")) >= 0.62 for ex in out):
                continue
            out.append({
                "topic": topic_guess,
                "fact": n["title"],
                "source_type": "news",
                "source": n.get("link", "")
            })
            seen.add(key)
            topic_count[topic_guess] = topic_count.get(topic_guess, 0) + 1

    return out


def confidence_level(news_count, yt_count, keyword_count):
    if news_count >= 12 and yt_count >= 10 and keyword_count >= 10:
        return "high"
    if news_count >= 6 and keyword_count >= 6:
        return "medium"
    return "low"


def jaccard_tokens(a: str, b: str):
    sa, sb = set(tokenize(a)), set(tokenize(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def dedupe_news_items(news_items, sim_threshold=0.55):
    deduped = []
    for n in news_items:
        title = n.get("title", "")
        is_dup = False
        for d in deduped:
            if jaccard_tokens(title, d.get("title", "")) >= sim_threshold:
                is_dup = True
                break
        if not is_dup:
            deduped.append(n)
    return deduped


def has_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text or ""))


def research_agent():
    news_items_all = []
    rss_errors = []
    for url in NEWS_RSS:
        try:
            root = fetch_xml(url)
            news_items_all.extend(parse_rss_items(root, limit=10))
        except Exception as e:
            rss_errors.append({"url": url, "error": str(e)})

    # 한국어 소스 비중 90% 목표
    kr_news = [n for n in news_items_all if has_korean(n.get("title", ""))]
    non_kr_news = [n for n in news_items_all if not has_korean(n.get("title", ""))]

    # KR 90% 이상 강제 + 모수 확대
    base_total = min(max(len(kr_news), 24), 70)
    non_kr_cap = max(2, int(base_total * 0.1))

    selected_news = kr_news[:base_total]
    selected_news.extend(non_kr_news[:non_kr_cap])
    selected_news = dedupe_news_items(selected_news, sim_threshold=0.58)

    yt_items = []
    yt_errors = []
    for feed_url in YOUTUBE_SIGNAL_FEEDS:
        try:
            root = fetch_xml(feed_url)
            yt_items.extend(parse_atom_entries(root, limit=6))
        except Exception as e:
            yt_errors.append({"feed": feed_url, "error": str(e)})

    keywords = extract_keywords(selected_news, yt_items, topk=20)
    selected_topics = select_topics(keywords, selected_news, max_topics=4)
    selected_topic = selected_topics[0]
    news_summary = summarize_news_facts(selected_news, selected_topics, limit_per_topic=4, total_limit=12)
    confidence = confidence_level(len(selected_news), len(yt_items), len(keywords))

    kr_ratio = (len([n for n in selected_news if has_korean(n.get("title", ""))]) / len(selected_news)) if selected_news else 0.0

    return {
        "selected_topic": selected_topic,
        "selected_topics": selected_topics,
        "keywords": keywords,
        "news_summary": news_summary,
        "confidence": confidence,
        "signals": {
            "news_count": len(selected_news),
            "youtube_signal_count": len(yt_items),
            "kr_news_ratio": round(kr_ratio, 3),
            "topic_count": len(selected_topics),
            "fact_count": len(news_summary),
            "rss_errors": rss_errors,
            "youtube_errors": yt_errors,
            "youtube_note": "유튜브는 제목/설명 기반 트렌드 신호로만 사용, 직접 인용 금지"
        }
    }


def planner(research):
    topic = research.get("selected_topic", "금융 이슈")
    k = research.get("keywords", [])[:4]
    return {
        "hook": f"지금 시장에서 놓치기 쉬운 {topic}, 핵심만 30초로 보겠습니다.",
        "core": [
            f"키워드 흐름: {', '.join(k) if k else '거시지표'}",
            "핵심 뉴스 3건에서 공통으로 반복되는 포인트",
            "개인에게 미칠 수 있는 실질 영향(지출/환율/금리)"
        ],
        "cta": "지금은 방향성 예측보다 내 리스크 노출 점검이 우선입니다."
    }


def script_agent(plan, research):
    facts = [n.get("fact", "") for n in research.get("news_summary", [])]
    facts_text = "\n".join([f"- {f}" for f in facts])
    return {
        "draft_script": f"""[Hook]\n{plan['hook']}\n\n[Core]\n{plan['core'][0]}\n{plan['core'][1]}\n{plan['core'][2]}\n\n[News Facts]\n{facts_text}\n\n[CTA]\n{plan['cta']}"""
    }


def deep_verifier(draft):
    script = draft["draft_script"]
    issues = []

    risky_phrases = ["무조건", "확정 수익", "반드시 오른다", "100%", "지금 사야", "원금 보장"]
    for p in risky_phrases:
        if p in script:
            issues.append({"type": "overclaim", "phrase": p, "fix": "단정 표현 완화"})

    if "News Facts" not in script:
        issues.append({"type": "fact_traceability", "phrase": "news facts missing", "fix": "근거 뉴스 문장 포함"})

    # 숫자/날짜 일치성 1차 점검 (문맥 없는 단정 수치 탐지)
    number_hits = re.findall(r"\d+[\.,]?\d*%?|\d+년|\d+월|\d+일", script)
    for n in number_hits:
        if "News Facts" in script and n not in script.split("[News Facts]")[-1]:
            issues.append({"type": "number_context", "phrase": n, "fix": "해당 수치의 근거 문장 추가 또는 표현 완화"})

    risk_level = "Low"
    if any(i["type"] in {"fact_traceability", "number_context"} for i in issues):
        risk_level = "High"
    elif issues:
        risk_level = "Medium"

    fixed = script
    for it in issues:
        if it["type"] == "overclaim":
            fixed = fixed.replace(it["phrase"], "가능성이 있습니다")

    return {
        "issues": issues,
        "risk_level": risk_level,
        "fixed_script": fixed,
        "rationale": "Codex 직접 검증 모드(외부 검증 API 미사용)"
    }


def legal_risk_agent(script_text: str):
    banned = ["투자 추천", "매수하세요", "지금 사세요", "수익 보장"]
    out = script_text
    for b in banned:
        out = out.replace(b, "신중히 검토하세요")
    return {
        "risk_level": "Low",
        "final_script": out + "\n\n" + DISCLAIMER
    }


def subtitle_agent(script_text: str):
    lines = [l.strip() for l in script_text.splitlines() if l.strip()]
    blocks = []
    t = 0
    idx = 1
    for line in lines:
        chunks = re.findall(r".{1,28}(?:\s|$)", line)
        chunks = [c.strip() for c in chunks if c.strip()]
        for c in chunks:
            start = f"00:00:{t:02d},000"
            end = f"00:00:{t+3:02d},000"
            blocks.append(f"{idx}\n{start} --> {end}\n{c}\n")
            idx += 1
            t += 3
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
        save_json(BASE / "logs" / f"run-{run_id}.json", {
            "status": "stopped",
            "reason": "risk_high",
            "time": datetime.now(timezone.utc).isoformat()
        })
        return

    legal = legal_risk_agent(verified["fixed_script"])
    save_json(BASE / "metadata" / "legal_risk.json", legal)

    (BASE / "outputs" / "script_final.md").write_text(legal["final_script"])
    srt = subtitle_agent(legal["final_script"])
    (BASE / "subtitles" / "latest.srt").write_text(srt)

    save_json(BASE / "logs" / f"run-{run_id}.json", {
        "status": "completed",
        "risk_level": legal["risk_level"],
        "time": datetime.now(timezone.utc).isoformat(),
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
