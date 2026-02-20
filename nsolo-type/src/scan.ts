import './styles.css';
import { extractFeatures, scoreFromFeatures } from './score';
import type { Gender } from './types';

const upload = document.querySelector<HTMLInputElement>('#upload')!;
const gender = document.querySelector<HTMLSelectElement>('#gender')!;
const canvas = document.querySelector<HTMLCanvasElement>('#preview')!;
const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
const btn = document.querySelector<HTMLButtonElement>('#analyze')!;
const status = document.querySelector<HTMLElement>('#status')!;

let loaded = false;

function drawCenterCover(img: HTMLImageElement) {
  const s = Math.min(img.width, img.height);
  const sx = (img.width - s) / 2;
  const sy = (img.height - s) / 2;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, sx, sy, s, s, 0, 0, canvas.width, canvas.height);
}

async function drawFaceCropIfAvailable(img: HTMLImageElement) {
  const AnyFaceDetector = (window as any).FaceDetector;
  if (!AnyFaceDetector) {
    drawCenterCover(img);
    return;
  }

  const fd = new AnyFaceDetector({ fastMode: true, maxDetectedFaces: 1 });
  const faces = await fd.detect(img);
  if (!faces?.length) {
    drawCenterCover(img);
    return;
  }

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
  const g = gender.value as Gender;
  const w = 224, h = 224;
  const off = document.createElement('canvas');
  off.width = w;
  off.height = h;
  off.getContext('2d')!.drawImage(canvas, 0, 0, w, h);
  const data = off.getContext('2d')!.getImageData(0, 0, w, h);
  const features = extractFeatures(data);
  const top3 = scoreFromFeatures(features, g).map(r => ({ ...r, p: Math.round(r.p * 1000) / 10 }));
  sessionStorage.setItem('nsolo_result', JSON.stringify(top3));
  sessionStorage.setItem('nsolo_gender', g);
  window.location.href = '/result.html';
};
