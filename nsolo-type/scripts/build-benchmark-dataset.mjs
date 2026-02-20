import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import path from 'node:path';
import { NAME_TYPES } from '../dist-types.mjs';

const OUT_DIR = 'benchmark/dataset';
const META_PATH = 'benchmark/dataset/metadata.json';

function run(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
}

function sanitize(s) {
  return s.replaceAll(/[^a-zA-Z0-9가-힣_-]/g, '_');
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  const rows = [];

  for (const t of NAME_TYPES) {
    const query = `나는솔로 ${t.label}`;
    const lines = run(`yt-dlp --flat-playlist --print "%(id)s\t%(title)s" "ytsearch6:${query}"`)
      .trim()
      .split('\n')
      .filter(Boolean);

    let n = 0;
    for (const line of lines) {
      if (n >= 3) break;
      const [id, title] = line.split('\t');
      if (!id) continue;
      const imageUrl = `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
      const fileName = `${t.slug}_${String(n + 1).padStart(2, '0')}.jpg`;
      const outPath = path.join(OUT_DIR, fileName);
      if (!existsSync(outPath)) {
        try {
          run(`curl -L --fail -s "${imageUrl}" -o "${outPath}"`);
        } catch {
          continue;
        }
      }
      rows.push({
        file: outPath,
        slug: t.slug,
        label: t.label,
        gender: t.gender,
        source: imageUrl,
        ref: `https://www.youtube.com/watch?v=${id}`,
        title: title || ''
      });
      n += 1;
    }
  }

  await writeFile(META_PATH, JSON.stringify({ createdAt: new Date().toISOString(), samples: rows }, null, 2));
  console.log(`saved ${rows.length} samples -> ${META_PATH}`);
}

main();