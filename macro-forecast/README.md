# Macro Forecast MVP

글로벌 매크로(환율/유가/실업률/CPI/정책금리) 신호를 바탕으로
미국/한국 주식 및 한국 주요 자산 방향성을 daily/weekly/monthly로 요약하는 MVP.

## 1차 범위
- 미국: NASDAQ, QQQ, 메가캡 기술주(AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA)
- 한국: KOSPI, USD/KRW, 주요 주도주(삼성전자, SK하이닉스, NAVER)
- 한국 부동산: 모멘텀 레이블 입력(초기엔 외부 입력값 기반)

## 제외 범위
- 자동매매/주문 실행
- DB 마이그레이션
- 배포 파이프라인

## 동작 개요
1. `data/sample_features.csv` 입력(지표별 변화율/레벨)
2. `signals.py`에서 자산별 방향 점수 계산
3. `report_templates.py`에서 daily/weekly/monthly markdown 생성

## 실행
```bash
python3 scripts/run_sample.py
```

출력:
- `outputs/daily.md`
- `outputs/weekly.md`
- `outputs/monthly.md`

## 테스트
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
