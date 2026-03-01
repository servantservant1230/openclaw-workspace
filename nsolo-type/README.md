# nsolo-type MVP

온디바이스 재미용 아키타입 분류 웹.

## run
- `npm install`
- `npm run dev`

## gate
- `npm run lint`
- `npm test`
- `npm run build`

## routes
- `/`
- `/scan.html` (광고/외부스크립트 없음)
- `/result.html` (AdSense)
- `/name/*.html` (AdSense)
- `/privacy.html`, `/terms.html`, `/about.html`, `/contact.html`

## deploy health check
- `./scripts/check-deploy-urls.sh`
- 커스텀 베이스 URL: `./scripts/check-deploy-urls.sh https://servantservant1230.github.io`
