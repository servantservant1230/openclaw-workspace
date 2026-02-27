# Telegram Polling Setup (No domain needed)

도메인/고정IP/포트포워딩 없이 `econodevkr_bot`을 운영하는 방법입니다.

## 1) 필수 환경변수
```bash
export TELEGRAM_BOT_TOKEN='YOUR_NEW_TOKEN'
```

## 2) Polling 프로세스 실행
```bash
cd /Volumes/WORK_SSD/workspace/macro-forecast
PYTHONPATH=src TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 scripts/run_telegram_polling.py
```

## 3) launchd 등록 (재부팅 후 자동 실행)
```bash
cd /Volumes/WORK_SSD/workspace/macro-forecast
./scripts/install_launchd.sh
```

제거:
```bash
cd /Volumes/WORK_SSD/workspace/macro-forecast
./scripts/uninstall_launchd.sh
```

## 4) 리포트 자동 발송 cron
```bash
cd /Volumes/WORK_SSD/workspace/macro-forecast
./scripts/install_cron_local.sh
```

## 5) 친구 사용법
- 친구가 `@econodevkr_bot` 열기
- `/start`
- `/subscribe daily|weekly|monthly|all`

## 참고
- Polling 모드에서는 webhook 설정이 필요 없습니다.
- 이 모드에서는 `run_telegram_polling.py`를 상시 실행해야 합니다.
