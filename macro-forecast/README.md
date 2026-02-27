# Macro Forecast MVP

글로벌 매크로(환율/유가/실업률/CPI/정책금리) 신호를 바탕으로
미국/한국 주식 및 한국 주요 자산 방향성을 daily/weekly/monthly로 요약하는 MVP.

## 1차+2차 범위
- 미국: NASDAQ, QQQ, 메가캡 기술주(AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA)
- 한국: KOSPI, USD/KRW, 주요 주도주(삼성전자, SK하이닉스, NAVER)
- 한국 부동산: 모멘텀 레이블 입력(초기엔 외부 입력값 기반)
- 백테스트(샘플): 타깃별 방향 정확도/전체 정확도 + 롤링 윈도우
- 종목 민감도 스냅샷: 주요 팩터 기여도 상위값
- 월간 시나리오: 자산군별 Bull/Base/Bear 자동 생성

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
```

참고:
- `run_live_or_sample.py`는 실시간 레벨 스냅샷을 시도합니다.
- `FRED_API_KEY`가 있으면 일부 거시지표(FRED)를 보강하고, 없어도 동작합니다.

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
