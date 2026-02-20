import { readFile, writeFile } from 'node:fs/promises';
import { Jimp } from 'jimp';
import { extractFeatures, extractFeaturesLegacy, scoreFromFeatures, scoreFromFeaturesLegacy, scoreFromFeaturesTuned } from '../src/score';

type Sample = { file: string; slug: string; gender: 'male' | 'female'; source: string; ref: string };

function topKHit(pred: { slug: string }[], answer: string, k: number) {
  return pred.slice(0, k).some(p => p.slug === answer) ? 1 : 0;
}

function summarize(rows: Array<{ top1: number; top3: number }>) {
  const n = rows.length || 1;
  return {
    top1: rows.reduce((a, b) => a + b.top1, 0) / n,
    top3: rows.reduce((a, b) => a + b.top3, 0) / n,
    n
  };
}

async function toImageData(file: string) {
  const img = await Jimp.read(file);
  img.cover({ w: 256, h: 256 });
  const { data, width, height } = img.bitmap;
  return { data: new Uint8ClampedArray(data), width, height } as unknown as ImageData;
}

async function run() {
  const meta = JSON.parse(await readFile('benchmark/dataset/metadata.json', 'utf8')) as { samples: Sample[] };
  const rows = [] as Array<{ slug: string; gender: 'male' | 'female'; top1: number; top3: number; top1L1: number; top3L1: number; top1L2: number; top3L2: number }>;

  for (const s of meta.samples) {
    const img = await toImageData(s.file);
    const fLegacy = extractFeaturesLegacy(img);
    const f = extractFeatures(img);

    const base = scoreFromFeaturesLegacy(fLegacy, s.gender);
    const l1 = scoreFromFeaturesTuned(f, s.gender, 0.68, 0.32);
    const l2 = scoreFromFeaturesTuned(f, s.gender, 0.55, 0.45);

    rows.push({
      slug: s.slug,
      gender: s.gender,
      top1: topKHit(base, s.slug, 1),
      top3: topKHit(base, s.slug, 3),
      top1L1: topKHit(l1, s.slug, 1),
      top3L1: topKHit(l1, s.slug, 3),
      top1L2: topKHit(l2, s.slug, 1),
      top3L2: topKHit(l2, s.slug, 3)
    });
  }

  const baseM = summarize(rows.map(r => ({ top1: r.top1, top3: r.top3 })));
  const l1M = summarize(rows.map(r => ({ top1: r.top1L1, top3: r.top3L1 })));
  const l2M = summarize(rows.map(r => ({ top1: r.top1L2, top3: r.top3L2 })));

  const md = `# 나는솔로 이름타입 벤치마크\n\n- 샘플 수: ${baseM.n}장 (타입별 3장)\n- 출처: YouTube 공개 썸네일(hqdefault.jpg), 쿼리=\"나는솔로 {이름타입}\"\n- 파일: benchmark/dataset/metadata.json\n\n## 정확도 비교\n\n| 버전 | Top1 | Top3 |\n|---|---:|---:|\n| Baseline(기존 score) | ${(baseM.top1 * 100).toFixed(1)}% | ${(baseM.top3 * 100).toFixed(1)}% |\n| Loop1(alpha=0.68,beta=0.32) | ${(l1M.top1 * 100).toFixed(1)}% | ${(l1M.top3 * 100).toFixed(1)}% |\n| Loop2(alpha=0.55,beta=0.45) | ${(l2M.top1 * 100).toFixed(1)}% | ${(l2M.top3 * 100).toFixed(1)}% |\n\n## 비고\n- Loop1: z-score 정규화 + proto 비중 상향 1차\n- Loop2: proto 비중 추가 상향 2차\n`;

  await writeFile('benchmark/metrics.md', md);
  await writeFile('benchmark/metrics.json', JSON.stringify({ baseline: baseM, loop1: l1M, loop2: l2M }, null, 2));
  console.log(md);
}

run();