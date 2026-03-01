#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://servantservant1230.github.io}"

URLS=(
  "/"
  "/about.html"
  "/privacy.html"
  "/terms.html"
  "/contact.html"
  "/faq.html"
  "/sitemap.xml"
  "/robots.txt"
  "/ads.txt"
)

fail=0
for p in "${URLS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$p")
  echo "$code $p"
  if [[ "$code" != "200" ]]; then
    fail=1
  fi
done

if [[ $fail -ne 0 ]]; then
  echo "deploy url check failed"
  exit 1
fi

echo "deploy url check passed"
