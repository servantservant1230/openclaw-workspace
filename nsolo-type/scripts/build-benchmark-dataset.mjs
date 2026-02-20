import { mkdir, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import path from 'node:path';
import { NAME_TYPES } from '../dist-types.mjs';

const OUT_DIR = 'benchmark/dataset';
const META_PATH = 'benchmark/dataset/metadata.json';
const TARGET_PER_TYPE = 20;
const SEARCH_POOL = 80;

function run(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
}

async function main() {
  await rm(OUT_DIR, { recursive: true, force: true });
  await mkdir(OUT_DIR, { recursive: true });

  const rows = [];

  for (const t of NAME_TYPES) {
    const query = `나는솔로 ${t.label}`;
    const raw = run(`yt-dlp --flat-playlist --print "%(id)s\t%(title)s" "ytsearch${SEARCH_POOL}:${query}"`)
      .trim()
      .split('\n')
      .filter(Boolean);

    const seen = new Set();
    let n = 0;

    for (const line of raw) {
      if (n >= TARGET_PER_TYPE) break;
      const [id, title = ''] = line.split('\t');
      if (!id || seen.has(id)) continue;
      seen.add(id);

      const imageUrl = `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
      const fileName = `${t.slug}_${String(n + 1).padStart(2, '0')}.jpg`;
      const outPath = path.join(OUT_DIR, fileName);

      try {
        if (!existsSync(outPath)) run(`curl -L --fail -s "${imageUrl}" -o "${outPath}"`);
        rows.push({
          file: outPath,
          slug: t.slug,
          label: t.label,
          gender: t.gender,
          source: imageUrl,
          ref: `https://www.youtube.com/watch?v=${id}`,
          title
        });
        n += 1;
      } catch {
        // skip bad thumbnail/url
      }
    }

    console.log(`${t.slug}: ${n}/${TARGET_PER_TYPE}`);
  }

  await writeFile(
    META_PATH,
    JSON.stringify(
      {
        createdAt: new Date().toISOString(),
        targetPerType: TARGET_PER_TYPE,
        samples: rows
      },
      null,
      2
    )
  );

  console.log(`saved ${rows.length} samples -> ${META_PATH}`);
}

main();
