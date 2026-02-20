import './styles.css';
import { extractFeatures, scoreFromFeatures } from './score';

const video = document.querySelector<HTMLVideoElement>('#video')!;
const canvas = document.querySelector<HTMLCanvasElement>('#preview')!;
const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
const btn = document.querySelector<HTMLButtonElement>('#analyze')!;
const status = document.querySelector<HTMLElement>('#status')!;
let stream: MediaStream | null = null;
let raf = 0;

function toGrayEdge(img: ImageData) {
  const d = img.data;
  const gray = new Uint8ClampedArray(img.width * img.height);
  for (let i = 0, p = 0; i < d.length; i += 4, p++) gray[p] = (d[i] * 0.3 + d[i + 1] * 0.59 + d[i + 2] * 0.11) | 0;
  const out = new Uint8ClampedArray(gray.length);
  const w = img.width, h = img.height;
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const gx = -gray[i - w - 1] + gray[i - w + 1] - 2 * gray[i - 1] + 2 * gray[i + 1] - gray[i + w - 1] + gray[i + w + 1];
      const gy = gray[i - w - 1] + 2 * gray[i - w] + gray[i - w + 1] - gray[i + w - 1] - 2 * gray[i + w] - gray[i + w + 1];
      out[i] = Math.min(255, Math.hypot(gx, gy));
    }
  }
  for (let i = 0, p = 0; i < d.length; i += 4, p++) {
    d[i] = d[i + 1] = d[i + 2] = out[p];
  }
  return img;
}

async function start() {
  stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 640, height: 480 }, audio: false });
  video.srcObject = stream;
  await video.play();
  status.textContent = '카메라 준비 완료';

  let last = 0;
  const loop = (t: number) => {
    if (t - last > 80) {
      last = t;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
      ctx.putImageData(toGrayEdge(img), 0, 0);
    }
    raf = requestAnimationFrame(loop);
  };
  raf = requestAnimationFrame(loop);
}

btn.onclick = () => {
  const w = 224, h = 224;
  const off = document.createElement('canvas');
  off.width = w; off.height = h;
  off.getContext('2d')!.drawImage(video, 0, 0, w, h);
  const data = off.getContext('2d')!.getImageData(0, 0, w, h);
  const features = extractFeatures(data);
  const top3 = scoreFromFeatures(features).map(r => ({ ...r, p: Math.round(r.p * 1000) / 10 }));
  sessionStorage.setItem('nsolo_result', JSON.stringify(top3));
  window.location.href = '/result.html';
};

window.addEventListener('beforeunload', () => {
  cancelAnimationFrame(raf);
  stream?.getTracks().forEach(t => t.stop());
});

start().catch(() => status.textContent = '카메라 권한이 필요합니다.');
