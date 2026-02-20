import { readFile, writeFile } from 'node:fs/promises';
import { Jimp } from 'jimp';
import { extractFeatures, scoreFromFeaturesTuned } from '../src/score';

type Sample = { file: string; slug: string; gender: 'male' | 'female' };

function topKHit(pred: { slug: string }[], answer: string, k: number) {
  return pred.slice(0, k).some(p => p.slug === answer) ? 1 : 0;
}

async function toImageData(file: string) {
  const img = await Jimp.read(file);
  img.cover({ w: 256, h: 256 });
  const { data, width, height } = img.bitmap;
  return { data: new Uint8ClampedArray(data), width, height } as unknown as ImageData;
}

async function main() {
  const meta = JSON.parse(await readFile('benchmark/dataset/metadata.json', 'utf8')) as { samples: Sample[] };
  const cache: Array<{ slug: string; gender: 'male'|'female'; f: number[] }> = [];

  for (const s of meta.samples) {
    const img = await toImageData(s.file);
    cache.push({ slug: s.slug, gender: s.gender, f: extractFeatures(img) });
  }

  let best = { alpha: 0.68, beta: 0.32, top1: 0, top3: 0 };
  const rows: any[] = [];

  for (let a = 0.4; a <= 0.8; a += 0.05) {
    const alpha = Math.round(a * 100) / 100;
    const beta = Math.round((1 - alpha) * 100) / 100;
    let t1 = 0, t3 = 0;
    for (const c of cache) {
      const pred = scoreFromFeaturesTuned(c.f, c.gender, alpha, beta);
      t1 += topKHit(pred, c.slug, 1);
      t3 += topKHit(pred, c.slug, 3);
    }
    const top1 = t1 / cache.length;
    const top3 = t3 / cache.length;
    rows.push({ alpha, beta, top1, top3 });
    if (top1 > best.top1 || (top1 === best.top1 && top3 > best.top3)) best = { alpha, beta, top1, top3 };
  }

  await writeFile('benchmark/tune-grid.json', JSON.stringify({ best, rows }, null, 2));
  console.log(`best alpha=${best.alpha}, beta=${best.beta}, top1=${(best.top1*100).toFixed(1)}%, top3=${(best.top3*100).toFixed(1)}%`);
}

main();
