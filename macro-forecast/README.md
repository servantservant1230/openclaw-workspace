# Macro Forecast MVP

> Telegram bot: `@econodevkr_bot` (subscription model)

글로벌 매크로(환율/유가/실업률/CPI/정책금리) 신호를 바탕으로
미국/한국 주식 및 한국 주요 자산 방향성을 daily/weekly/monthly로 요약하는 MVP.

## 1차+2차 범위
- 미국: NASDAQ, QQQ, 메가캡 기술주(AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA)
- 한국: KOSPI, USD/KRW, 주요 주도주(삼성전자, SK하이닉스, NAVER)
- 한국 부동산: 모멘텀 레이블 입력(초기엔 외부 입력값 기반)
- 백테스트(샘플): 타깃별 방향 정확도/전체 정확도 + 롤링 윈도우
- 종목 민감도 스냅샷: 주요 팩터 기여도 상위값
- 월간 시나리오: 자산군별 Bull/Base/Bear 자동 생성
- 신뢰도 태그: LOW/MED/HIGH confidence 표시
- 월간 핵심 지표 요약 자동 삽입
- 구독 모델(채널/대상/cadence) + 발송 큐 생성

## 제외 범위
- 자동매매/주문 실행
- DB 마이그레이션
- 배포 파이프라인

## 동작 개요
1. `data/sample_features.csv` 입력(지표별 변화율/레벨)
2. `signals.py`에서 자산별 방향 점수 계산
3. `report_templates.py`에서 daily/weekly/monthly markdown 생성
4. `historical_sample.csv`로 샘플 백테스트 수행
5. 개별 종목 민감도 리포트 생성

## 실행
```bash
PYTHONPATH=src python3 scripts/run_sample.py
PYTHONPATH=src python3 scripts/run_live_or_sample.py
PYTHONPATH=src python3 scripts/backtest_sample.py
PYTHONPATH=src python3 scripts/rolling_backtest.py
PYTHONPATH=src python3 scripts/sensitivity_sample.py

# 구독 등록(운영자 수동)
PYTHONPATH=src python3 scripts/subscription_cli.py add --channel telegram --target <chat_id> --cadence all

# 채팅 명령 처리(사용자 self-subscribe)
PYTHONPATH=src python3 scripts/handle_subscription_command.py --channel telegram --target <chat_id> --text "/subscribe all"

# cadence별 발송 큐 생성(옵션)
PYTHONPATH=src python3 scripts/build_dispatch_queue.py daily

# 텔레그램 실제 발송 (토큰은 환경변수)
PYTHONPATH=src TELEGRAM_BOT_TOKEN="..." python3 scripts/send_telegram_reports.py daily
```

참고:
- `run_live_or_sample.py`는 실시간 레벨 스냅샷을 시도합니다.
- `FRED_API_KEY`가 있으면 일부 거시지표(FRED)를 보강하고, 없어도 동작합니다.
- 구독 방식은 "채널에서 이미 대화 중인 대상" 기준으로 저장하므로, 별도 봇 ID를 매번 수동 입력하는 절차를 최소화할 수 있습니다.

출력:
- `outputs/daily.md`
- `outputs/weekly.md`
- `outputs/monthly.md`
- `outputs/backtest_metrics.json`
- `outputs/backtest_summary.md`
- `outputs/stock_sensitivity.md`

## 테스트
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```
