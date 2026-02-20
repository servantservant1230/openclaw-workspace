import { Gender, NAME_TYPES } from './types';

export function softmax(arr: number[]): number[] {
  const m = Math.max(...arr);
  const ex = arr.map(v => Math.exp(v - m));
  const s = ex.reduce((a, b) => a + b, 0);
  return ex.map(v => v / s);
}

const LEGACY_WEIGHTS: number[][] = NAME_TYPES.map((_, i) => [
  Math.sin(i + 1) * 0.8,
  Math.cos(i + 2) * 0.7,
  Math.sin(i + 3) * 0.6,
  Math.cos(i + 4) * 0.5,
  Math.sin(i + 5) * 0.4,
  Math.cos(i + 6) * 0.3,
  Math.sin(i + 7) * 0.2,
  Math.cos(i + 8) * 0.1
]);

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

const PROTO: number[][] = NAME_TYPES.map((_, i) => [
  Math.sin(i * 0.61),
  Math.cos(i * 0.73),
  Math.sin(i * 0.47),
  Math.cos(i * 0.59),
  Math.sin(i * 0.31),
  Math.cos(i * 0.43),
  Math.sin(i * 0.23),
  Math.cos(i * 0.17)
]);

function dot(a: number[], b: number[]) {
  let s = 0;
  for (let i = 0; i < 8; i++) s += (a[i] ?? 0) * (b[i] ?? 0);
  return s;
}

function zNorm(f: number[]) {
  const mean = f.reduce((a, b) => a + b, 0) / f.length;
  const variance = f.reduce((a, b) => a + (b - mean) ** 2, 0) / f.length;
  const sd = Math.sqrt(variance) || 1;
  return f.map(v => (v - mean) / sd);
}

function rawFromFeatures(features: number[], alpha = 0.68, beta = 0.32) {
  const zn = zNorm(features);
  return WEIGHTS.map((w, i) => alpha * dot(w, zn) + beta * dot(PROTO[i], zn));
}

export function scoreFromFeaturesLegacy(features: number[], gender: Gender) {
  const raw = LEGACY_WEIGHTS.map(w => w.reduce((acc, v, idx) => acc + v * (features[idx] ?? 0), 0));
  const probs = softmax(raw);
  return NAME_TYPES
    .map((t, i) => ({ ...t, p: probs[i] }))
    .filter(r => r.gender === gender)
    .sort((a, b) => b.p - a.p)
    .slice(0, 3);
}

export function scoreFromFeatures(features: number[], gender: Gender) {
  const probs = softmax(rawFromFeatures(features));
  return NAME_TYPES
    .map((t, i) => ({ ...t, p: probs[i] }))
    .filter(r => r.gender === gender)
    .sort((a, b) => b.p - a.p)
    .slice(0, 3);
}

export function scoreFromFeaturesTuned(features: number[], gender: Gender, alpha: number, beta: number) {
  const probs = softmax(rawFromFeatures(features, alpha, beta));
  return NAME_TYPES
    .map((t, i) => ({ ...t, p: probs[i] }))
    .filter(r => r.gender === gender)
    .sort((a, b) => b.p - a.p)
    .slice(0, 3);
}

export function extractFeaturesLegacy(data: ImageData): number[] {
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

export function extractFeatures(data: ImageData): number[] {
  const d = data.data;
  let mean = 0, edge = 0, left = 0, right = 0, sat = 0;
  const px = d.length / 4;
  const w = data.width;
  for (let i = 0; i < d.length; i += 4) {
    const r = d[i], g = d[i + 1], b = d[i + 2];
    const y = 0.299 * r + 0.587 * g + 0.114 * b;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    mean += y;
    sat += max === 0 ? 0 : (max - min) / max;
    const x = ((i / 4) % w);
    if (x < w / 2) left += y; else right += y;
    if (i > 4) edge += Math.abs(y - (0.299 * d[i - 4] + 0.587 * d[i - 3] + 0.114 * d[i - 2]));
  }
  mean /= px;
  left /= px / 2;
  right /= px / 2;
  sat /= px;
  const contrast = Math.abs(left - right) / 255;
  return [
    mean / 255,
    (left - right) / 255,
    edge / (px * 255),
    (left + right) / (2 * 255),
    sat,
    contrast,
    Math.sin(edge / 100),
    Math.cos(mean / 50)
  ];
}
