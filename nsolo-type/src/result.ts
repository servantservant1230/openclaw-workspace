import './styles.css';

type Row = { slug: string; label: string; desc: string; p: number };
const root = document.querySelector('#result')!;
const data = sessionStorage.getItem('nsolo_result');

function makeShareCard(top3: Row[]) {
  const c = document.createElement('canvas');
  c.width = 1080;
  c.height = 1350;
  const x = c.getContext('2d')!;

  x.fillStyle = '#0f172a';
  x.fillRect(0, 0, c.width, c.height);

  x.fillStyle = '#ffffff';
  x.font = 'bold 56px system-ui';
  x.fillText('나는솔로 타입 결과', 80, 140);

  x.font = '42px system-ui';
  top3.forEach((r, i) => {
    x.fillText(`${i + 1}. ${r.label}  ${r.p}%`, 80, 250 + i * 110);
    x.font = '30px system-ui';
    x.fillStyle = '#cbd5e1';
    x.fillText(r.desc, 120, 295 + i * 110);
    x.font = '42px system-ui';
    x.fillStyle = '#ffffff';
  });

  x.fillStyle = '#94a3b8';
  x.font = '28px system-ui';
  x.fillText('오락용 아키타입 분류 · 실존 인물 식별 아님', 80, 1240);

  return c.toDataURL('image/png');
}

if (!data) {
  root.innerHTML = '<p>결과가 없습니다. 다시 분석해주세요.</p>';
} else {
  const rows: Row[] = JSON.parse(data);
  root.innerHTML = rows
    .map(
      (r, i) => `
    <div class="card">
      <small class="muted">${i + 1}순위</small>
      <div class="result-top">${r.label} <span class="muted" style="font-size:22px">${r.p}%</span></div>
      <p>${r.desc}</p>
      <div class="bar"><i style="width:${r.p}%"></i></div>
      <p><a href="/name/${r.slug}.html">${r.label} 타입 설명 보기</a></p>
    </div>`
    )
    .join('');

  const top = rows[0];
  const shareText = `내 나는솔로 타입은 ${top.label} (${top.p}%)!`;
  (document.querySelector('#share') as HTMLButtonElement).onclick = async () => {
    if (navigator.share) await navigator.share({ text: shareText, url: location.href });
    else await navigator.clipboard.writeText(shareText);
  };

  (document.querySelector('#save-card') as HTMLButtonElement).onclick = () => {
    const url = makeShareCard(rows);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'nsolo-result.png';
    a.click();
  };
}
