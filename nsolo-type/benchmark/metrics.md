# 나는솔로 이름타입 벤치마크

- 샘플 수: 240장 (타입별 20장)
- 출처: YouTube 공개 썸네일(hqdefault.jpg), 쿼리="나는솔로 {이름타입}"
- 파일: benchmark/dataset/metadata.json

## 정확도 비교

| 버전 | Top1 | Top3 |
|---|---:|---:|
| Baseline(기존 score) | 12.9% | 46.7% |
| Loop1(alpha=0.68,beta=0.32) | 15.8% | 47.5% |
| Loop2(alpha=0.55,beta=0.45) | 15.0% | 50.0% |

## 비고
- Loop1: z-score 정규화 + proto 비중 상향 1차
- Loop2: proto 비중 추가 상향 2차
