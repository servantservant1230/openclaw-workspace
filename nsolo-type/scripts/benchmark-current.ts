import { readFile } from 'node:fs/promises';
import { Jimp } from 'jimp';
import { extractFeatures, scoreFromFeatures } from '../src/score';

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
  const boosted = new Set(['oksoon', 'hyunsook', 'youngja', 'youngho', 'youngsik', 'youngchul']);
  const meta = JSON.parse(await readFile('benchmark/dataset/metadata.json', 'utf8')) as { samples: Sample[] };

  let t1 = 0, t2 = 0, t3 = 0;
  let boostedTop1 = 0;

  for (const s of meta.samples) {
    const img = await toImageData(s.file);
    const pred = scoreFromFeatures(extractFeatures(img), s.gender);
    t1 += topKHit(pred, s.slug, 1);
    t2 += topKHit(pred, s.slug, 2);
    t3 += topKHit(pred, s.slug, 3);
    if (boosted.has(pred[0]?.slug)) boostedTop1 += 1;
  }

  const n = meta.samples.length;
  const pct = (v: number) => `${(v * 100 / n).toFixed(1)}%`;
  console.log(JSON.stringify({
    n,
    top1: pct(t1),
    top2: pct(t2),
    top3: pct(t3),
    boostedTop1Share: pct(boostedTop1)
  }, null, 2));
}

main();
