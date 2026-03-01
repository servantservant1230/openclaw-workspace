# AdSense Readiness (Pre-approval)

## 현재 전략
- 승인 전에는 광고 노출 스크립트를 강제 삽입하지 않음
- 먼저 콘텐츠/정책/신뢰 페이지 완성도를 높여 심사 통과 확률을 개선

## 체크리스트
- [x] About / Privacy / Terms 존재
- [x] robots.txt / sitemap.xml / ads.txt 존재
- [x] Contact 페이지 추가 (`/contact.html`)
- [x] Vite build input에 `contact.html` 포함 (배포 누락 방지)
- [x] 홈 네비게이션에서 Contact 접근 가능
- [ ] 배포 후 URL 헬스체크(`check-deploy-urls.sh`) 200 확인

## 승인 후 단계
1. AdSense 스크립트 (`adsbygoogle.js?client=...`) 삽입
2. 홈/결과 페이지에 슬롯 최소 배치
3. 과도한 광고 밀도 방지
4. Search Console/AdSense 크롤링 상태 확인
