import './styles.css';

type Row = { slug: string; label: string; desc: string; p: number };
const root = document.querySelector('#result')!;
const data = sessionStorage.getItem('nsolo_result');
if (!data) root.innerHTML = '<p>결과가 없습니다. 다시 분석해주세요.</p>';
else {
  const rows: Row[] = JSON.parse(data);
  root.innerHTML = rows.map((r, i) => `
    <div class="card">
      <h3>${i + 1}. ${r.label} (${r.p}%)</h3>
      <p>${r.desc}</p>
      <div class="bar"><i style="width:${r.p}%"></i></div>
      <p><a href="/name/${r.slug}.html">${r.label} 타입 설명 보기</a></p>
    </div>`).join('');

  const top = rows[0];
  const shareText = `내 나는솔로 타입은 ${top.label} (${top.p}%)!`; 
  (document.querySelector('#share') as HTMLButtonElement).onclick = async () => {
    if (navigator.share) await navigator.share({ text: shareText, url: location.href });
    else await navigator.clipboard.writeText(shareText);
  };
}
