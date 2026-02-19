# shorts-factory (MVP)

최신 금융 이슈 기반 쇼츠 자동생산 파이프라인.

## 1) A안 리서치 파이프라인 설계

ResearchAgent (가벼운 방식):
1. RSS 3~5개 수집
2. 금융 유튜버 제목/설명 수집(본문 분석 금지)
3. 키워드 빈도 분석
4. 상승 토픽 1~2개 추출
5. 관련 뉴스 3개 수집
6. JSON 구조화

출력(JSON):
```json
{
  "selected_topic": "...",
  "keywords": ["..."],
  "news_summary": [
    {"fact": "...", "source_type": "news"}
  ],
  "confidence": "low|medium|high"
}
```

## 2) MVP 코드 구조 제안

- `src/orchestrator.py`: 전체 플로우 제어 (Codex 오케스트레이터)
- `src/research_agent.py`: RSS+유튜브 메타 수집/키워드 추출
- `src/planner.py`: Hook/Core/CTA 설계
- `src/script_agent.py`: qwen 기반 스크립트 생성
- `src/deep_verifier.py`: Codex 사실/제도/논리 검증
- `src/legal_risk_agent.py`: 법적 리스크 필터 + 고지문
- `src/neutralizer.py`: 과장표현 완화
- `src/subtitle_agent.py`: SRT 변환
- `src/logger.py`: JSON 로그 저장

## 3) 실행 단계 정의

1. ResearchAgent 실행 → `research/latest.json`
2. Planner 실행 → `metadata/plan.json`
3. ScriptAgent 실행 → `outputs/script_draft.md`
4. DeepVerificationAgent 실행 → `metadata/verification.json`
5. LegalRiskAgent 실행 → `metadata/legal_risk.json`
6. 위험도 Low/Medium이면 계속, High면 중단/승인요청
7. Neutralizer 실행 → `outputs/script_final.md`
8. SubtitleAgent 실행 → `subtitles/latest.srt`
9. 로그 저장 → `logs/run-<timestamp>.json`

## 게이트
- 품질 게이트: 사실검증 통과 + 법적리스크 필터 통과
- 중단 조건: High risk / 제도 불확실 / 법적 분쟁 가능성 / API 예산 초과 / 플랫폼 정책 위반
