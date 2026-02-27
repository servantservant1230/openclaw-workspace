# Cron Setup (Telegram report delivery)

> 전제: `TELEGRAM_BOT_TOKEN`은 환경변수로만 주입 (코드/레포 저장 금지)

## 1) 스크립트 실행 권한
```bash
chmod +x macro-forecast/scripts/run_and_send.sh
```

## 2) 크론 등록
자동 등록 스크립트 사용:
```bash
./macro-forecast/scripts/install_cron.sh
```

수동 등록이 필요하면 아래 예시를 사용:
```cron
# Daily: 매일 08:30
30 8 * * * cd /Volumes/WORK_SSD/workspace && TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}" ./macro-forecast/scripts/run_and_send.sh daily >> /tmp/macro-forecast-daily.log 2>&1

# Weekly: 매주 월요일 08:40
40 8 * * 1 cd /Volumes/WORK_SSD/workspace && TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}" ./macro-forecast/scripts/run_and_send.sh weekly >> /tmp/macro-forecast-weekly.log 2>&1

# Monthly: 매월 1일 08:50
50 8 1 * * cd /Volumes/WORK_SSD/workspace && TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}" ./macro-forecast/scripts/run_and_send.sh monthly >> /tmp/macro-forecast-monthly.log 2>&1
```

## 3) 등록/확인
```bash
crontab -l
```

## 4) 수동 테스트
```bash
cd /Volumes/WORK_SSD/workspace/macro-forecast
PYTHONPATH=src TELEGRAM_BOT_TOKEN="..." python3 scripts/send_telegram_reports.py daily
```
