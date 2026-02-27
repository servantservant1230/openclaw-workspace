# ADR 0001: Agent Guardrails를 기본 운영 규칙으로 채택

- 상태: Accepted
- 날짜: 2026-02-27

## Context

자연어 기반 자율 개발 에이전트는 빠르지만, 실패 시 비용이 크다.
대표 리스크는 (1) 비밀 누출, (2) 파괴적 실행, (3) 검증 없는 허위 완료, (4) 범위 확장이다.

OpenClaw 공식 문서는 개인 비서 trust model에서 최소 권한·접근 통제·도구 제한·감사를 반복 권고한다.
또한 에이전트 운영에서 “복잡도 최소화 후 점진 확장” 원칙이 실무 성능(품질/디버깅/운영 안정성)에 유리하다는 업계 가이드가 일관적이다.

## Decision

다음 규칙을 MVP 기본값으로 채택한다.

1. **보안 우선**: 비밀/PII 출력·저장·커밋 금지.
2. **비가역 작업 금지**: main direct push/force push/대량 삭제/배포/DB 실행 금지.
3. **검증 강제**: 완료 전 테스트 또는 실행 증거 1개 이상 필수.
4. **작은 PR**: 기본 25 files / 800 lines 제한, 초과 시 분할.
5. **자연어 지시 구조화**: 모든 요청을 ticket으로 정규화.

## Why this improves performance

### 사실/근거 (Evidence)

- OpenClaw 보안 문서: 모델 자체보다 **접근 통제와 tool blast radius 제한**이 핵심 방어선임.
- OpenClaw 보안 감사 루틴: 설정 드리프트와 과권한을 자동 탐지/교정하도록 설계.
- Agent 운영 가이드(Anthropic 등): 단순한 워크플로에서 시작할수록 디버깅 가능성과 비용 예측성이 높음.
- 커뮤니티 사례: “완료라고 했지만 실제 미완료”, “관련 없는 대규모 변경”, “툴 과사용”이 반복됨.

### 실무 적용 (Practice)

- Guardrail은 속도를 늦추는 규제가 아니라, **재작업·사고 비용을 줄여 총 리드타임을 단축**한다.
- “작은 PR + 검증 증거”는 리뷰 품질과 롤백 속도를 높여 배포 신뢰성을 올린다.
- “Out-of-scope 명시”는 scope creep를 차단해 예측 가능한 일정 유지에 기여한다.

## Consequences

### Positive

- 보안 사고 및 실수성 파괴 작업 확률 감소
- 리뷰/롤백/감사 용이성 증가
- 완료 신뢰도 향상(증거 기반 커뮤니케이션)

### Trade-off

- 초기엔 체크리스트 비용이 소폭 증가
- 대형 기능은 PR 분할 관리가 필요

## References

### Official / primary

1. OpenClaw Docs – Agent Workspace: <https://docs.openclaw.ai/concepts/agent-workspace>
2. OpenClaw Docs – Gateway Security: <https://docs.openclaw.ai/gateway/security>
3. OpenClaw Security & Trust: <https://github.com/openclaw/openclaw/tree/main/security>
4. Anthropic – Building effective agents: <https://www.anthropic.com/engineering/building-effective-agents>

### Community cases (case-only, not universal)

5. Developer community threads (HN/Reddit) discussing failure modes such as lazy diffs, false completion, and over-broad edits.
