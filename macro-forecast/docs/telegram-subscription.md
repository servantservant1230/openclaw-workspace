# Telegram Subscription Flow (econodevkr_bot)

이 문서는 `econodevkr_bot` 구독형 리포트 흐름의 MVP 운영 방법을 설명합니다.

## 사용자 입장(친구)
1. 텔레그램에서 `@econodevkr_bot` 열기
2. `/start`
3. `/subscribe daily` 또는 `/subscribe all`
4. 해지: `/unsubscribe`
5. 상태: `/status`

## 시스템 입장(백엔드)
- 수신 명령을 `handle_subscription_command.py`로 처리
- 구독 상태는 `data/subscribers.json` 저장
- cadence별 리포트 발송 큐는 `build_dispatch_queue.py` 생성

## 예시
```bash
PYTHONPATH=src python3 scripts/handle_subscription_command.py --channel telegram --target 6830510658 --text "/subscribe all"
PYTHONPATH=src python3 scripts/build_dispatch_queue.py daily
```

## 보안 메모
- Bot token은 코드/리포지토리에 저장하지 말 것
- 토큰은 OpenClaw 설정 또는 안전한 시크릿 저장소에서만 관리
