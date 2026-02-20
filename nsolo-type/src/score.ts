import { Gender, NAME_TYPES } from './types';

export function softmax(arr: number[]): number[] {
  const m = Math.max(...arr);
  const ex = arr.map(v => Math.exp(v - m));
  const s = ex.reduce((a, b) => a + b, 0);
  return ex.map(v => v / s);
}

const WEIGHTS: number[][] = NAME_TYPES.map((_, i) => [
  Math.sin(i + 1) * 0.8,
  Math.cos(i + 2) * 0.7,
  Math.sin(i + 3) * 0.6,
  Math.cos(i + 4) * 0.5,
  Math.sin(i + 5) * 0.4,
  Math.cos(i + 6) * 0.3,
  Math.sin(i + 7) * 0.2,
  Math.cos(i + 8) * 0.1
]);

export function scoreFromFeatures(features: number[], gender: Gender) {
  const raw = WEIGHTS.map(w => w.reduce((acc, v, idx) => acc + v * (features[idx] ?? 0), 0));
  const probs = softmax(raw);
  const rows = NAME_TYPES
    .map((t, i) => ({ ...t, p: probs[i] }))
    .filter(r => r.gender === gender)
    .sort((a, b) => b.p - a.p)
    .slice(0, 3);
  return rows;
}

export function extractFeatures(data: ImageData): number[] {
  const d = data.data;
  let mean = 0, edge = 0, left = 0, right = 0;
  const px = d.length / 4;
  const w = data.width;
  for (let i = 0; i < d.length; i += 4) {
    const y = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    mean += y;
    const x = ((i / 4) % w);
    if (x < w / 2) left += y; else right += y;
    if (i > 4) edge += Math.abs(y - (0.299 * d[i - 4] + 0.587 * d[i - 3] + 0.114 * d[i - 2]));
  }
  mean /= px;
  left /= px / 2;
  right /= px / 2;
  return [
    mean / 255,
    (left - right) / 255,
    edge / (px * 255),
    (left + right) / (2 * 255),
    Math.sin(mean), Math.cos(mean), Math.sin(edge), Math.cos(edge)
  ];
}
