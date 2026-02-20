import './styles.css';
import { extractFeatures, scoreFromFeatures } from './score';
import type { Gender } from './types';

const upload = document.querySelector<HTMLInputElement>('#upload')!;
const genderValue = document.querySelector<HTMLInputElement>('#genderValue')!;
const genderButtons = Array.from(document.querySelectorAll<HTMLButtonElement>('[data-gender-btn]'));
const canvas = document.querySelector<HTMLCanvasElement>('#preview')!;
const btn = document.querySelector<HTMLButtonElement>('#analyze')!;
const status = document.querySelector<HTMLElement>('#status')!;
const ctx = canvas.getContext('2d', { willReadFrequently: true })!;

let loaded = false;

function calibrateDisplayTop3<T extends { p: number }>(rows: T[]) {
  // 결과 노출용 보정: 상위값은 조금 더 강조하고, Top3 합은 100으로 정규화
  const t = 0.72; // temperature (<1 이면 상위 확률 강조)
  const raw = rows.map(r => Math.pow(Math.max(r.p, 1e-6), 1 / t));
  const sum = raw.reduce((a, b) => a + b, 0) || 1;

  const pct = raw.map(v => (v / sum) * 100);
  const rounded = pct.map(v => Math.round(v * 10) / 10);

  // 반올림 오차를 1위에 보정해서 합을 정확히 100.0으로 맞춤
  const total = rounded.reduce((a, b) => a + b, 0);
  const diff = Math.round((100 - total) * 10) / 10;
  rounded[0] = Math.max(0, Math.round((rounded[0] + diff) * 10) / 10);

  return rows.map((r, i) => ({ ...r, p: rounded[i] }));
}

function applyGenderUI(selected: Gender) {
  genderValue.value = selected;
  genderButtons.forEach(b => {
    const active = b.dataset.gender === selected;
    b.classList.toggle('active', active);
    b.classList.toggle('secondary', active);
  });
}

genderButtons.forEach(b => {
  b.onclick = () => applyGenderUI((b.dataset.gender as Gender) || 'female');
});
applyGenderUI('female');

function drawCenterCover(img: HTMLImageElement) {
  const s = Math.min(img.width, img.height);
  const sx = (img.width - s) / 2;
  const sy = (img.height - s) / 2;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, sx, sy, s, s, 0, 0, canvas.width, canvas.height);
}

async function drawFaceCropIfAvailable(img: HTMLImageElement) {
  const AnyFaceDetector = (window as any).FaceDetector;
  if (!AnyFaceDetector) return drawCenterCover(img);
  const fd = new AnyFaceDetector({ fastMode: true, maxDetectedFaces: 1 });
  const faces = await fd.detect(img);
  if (!faces?.length) return drawCenterCover(img);

  const b = faces[0].boundingBox;
  const pad = 0.35;
  const cx = b.x + b.width / 2;
  const cy = b.y + b.height / 2;
  const side = Math.max(b.width, b.height) * (1 + pad * 2);
  const sx = Math.max(0, Math.min(img.width - side, cx - side / 2));
  const sy = Math.max(0, Math.min(img.height - side, cy - side / 2));

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, sx, sy, side, side, 0, 0, canvas.width, canvas.height);
}

upload.onchange = async () => {
  const file = upload.files?.[0];
  if (!file) return;

  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = async () => {
    try {
      await drawFaceCropIfAvailable(img);
      loaded = true;
      status.textContent = '사진 업로드 완료 (얼굴 중심 정렬)';
    } catch {
      drawCenterCover(img);
      loaded = true;
      status.textContent = '사진 업로드 완료';
    } finally {
      URL.revokeObjectURL(url);
    }
  };
  img.src = url;
};

btn.onclick = () => {
  if (!loaded) {
    status.textContent = '먼저 사진을 업로드해 주세요.';
    return;
  }

  btn.disabled = true;
  status.textContent = '분석 중...';

  const g = (genderValue.value as Gender) || 'female';
  const w = 224, h = 224;
  const off = document.createElement('canvas');
  off.width = w;
  off.height = h;
  off.getContext('2d')!.drawImage(canvas, 0, 0, w, h);

  const data = off.getContext('2d')!.getImageData(0, 0, w, h);
  const features = extractFeatures(data);
  const rawTop3 = scoreFromFeatures(features, g);
  const top3 = calibrateDisplayTop3(rawTop3);

  sessionStorage.setItem('nsolo_result', JSON.stringify(top3));
  sessionStorage.setItem('nsolo_gender', g);

  btn.disabled = false;
  window.location.href = '/result.html';
};
