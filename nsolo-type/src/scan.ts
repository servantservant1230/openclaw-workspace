import './styles.css';
import { extractFeatures, scoreFromFeatures } from './score';
import type { Gender } from './types';

const upload = document.querySelector<HTMLInputElement>('#upload')!;
const gender = document.querySelector<HTMLSelectElement>('#gender')!;
const canvas = document.querySelector<HTMLCanvasElement>('#preview')!;
const video = document.querySelector<HTMLVideoElement>('#video')!;
const btn = document.querySelector<HTMLButtonElement>('#analyze')!;
const captureBtn = document.querySelector<HTMLButtonElement>('#capture')!;
const status = document.querySelector<HTMLElement>('#status')!;
const ctx = canvas.getContext('2d', { willReadFrequently: true })!;

let loaded = false;
let stream: MediaStream | null = null;
let sourceMode: 'camera' | 'upload' = 'camera';

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

async function startFrontCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 640, height: 640 },
      audio: false
    });
    video.srcObject = stream;
    await video.play();
    sourceMode = 'camera';
    status.textContent = '전면 카메라 준비 완료. 캡처 후 분석하세요.';
  } catch {
    status.textContent = '카메라를 시작할 수 없어 업로드 모드로 전환합니다.';
    sourceMode = 'upload';
  }
}

captureBtn.onclick = () => {
  if (!video.videoWidth) {
    status.textContent = '카메라가 준비되지 않았습니다.';
    return;
  }
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  loaded = true;
  sourceMode = 'camera';
  status.textContent = '캡처 완료. 분석하기를 눌러주세요.';
};

upload.onchange = async () => {
  const file = upload.files?.[0];
  if (!file) return;

  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = async () => {
    try {
      await drawFaceCropIfAvailable(img);
      loaded = true;
      sourceMode = 'upload';
      status.textContent = '사진 업로드 완료 (얼굴 중심 정렬)';
    } catch {
      drawCenterCover(img);
      loaded = true;
      sourceMode = 'upload';
      status.textContent = '사진 업로드 완료';
    } finally {
      URL.revokeObjectURL(url);
    }
  };
  img.src = url;
};

btn.onclick = () => {
  btn.disabled = true;
  status.textContent = '분석 중...';

  const g = gender.value as Gender;
  const w = 224, h = 224;
  const off = document.createElement('canvas');
  off.width = w;
  off.height = h;
  const offCtx = off.getContext('2d')!;

  if (sourceMode === 'camera' && video.videoWidth) {
    offCtx.drawImage(video, 0, 0, w, h);
  } else {
    if (!loaded) {
      status.textContent = '먼저 캡처하거나 사진을 업로드해 주세요.';
      btn.disabled = false;
      return;
    }
    offCtx.drawImage(canvas, 0, 0, w, h);
  }

  const data = offCtx.getImageData(0, 0, w, h);
  const features = extractFeatures(data);
  const top3 = scoreFromFeatures(features, g).map(r => ({ ...r, p: Math.round(r.p * 1000) / 10 }));

  sessionStorage.setItem('nsolo_result', JSON.stringify(top3));
  sessionStorage.setItem('nsolo_gender', g);
  btn.disabled = false;
  window.location.href = '/result.html';
};

window.addEventListener('beforeunload', () => {
  stream?.getTracks().forEach(t => t.stop());
});

startFrontCamera();
