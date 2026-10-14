// „Szukasz miejsca na nagranie podcastu?” – przesuwanie kart jak w aplikacji randkowej. renderAt(t)
const D = window.DATA;
const stage = document.getElementById('stage');
const OR = '#FF592A', PK = '#FF2E7E', CR = '#F9EEE4', BG = '#1A0E18', NO = '#FF3B4E', YES = '#2BD67B';
const GRAD = `linear-gradient(135deg, ${OR}, ${PK})`;
const cl = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const oC = t => 1 - Math.pow(1 - cl(t), 3);
const oE = t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * cl(t)));
const iC = t => Math.pow(cl(t), 3);
const oB = (t, c1 = 1.8) => { t = cl(t); const c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
function hash(i, j) { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); }

const CARDS = [
  { e: '🪙', bg: 'linear-gradient(160deg,#F2B33D,#9A5B12)', name: 'Krypto od kuzyna', age: '19', km: '„tym razem na pewno”', tags: ['−87% od wtorku', 'sygnały na Telegramie'] },
  { e: '📘', bg: 'linear-gradient(160deg,#5B8CFF,#27409C)', name: 'E‑book o e‑bookach', age: '1', km: '„pasywny dochód”', tags: ['sprzedane: 2 sztuki', 'kupiła mama i ciocia'] },
  { e: '🙈', bg: 'linear-gradient(160deg,#47B5FF,#1A5FA8)', name: 'Konto „tylko dla fanów”', age: '', km: '„to tylko stopy”', tags: ['babcia obserwuje', 'szef też'] },
  { e: '📦', bg: 'linear-gradient(160deg,#A3A08F,#4E4B3E)', name: 'Dropshipping', age: '3', km: 'towar z drugiego końca świata', tags: ['dostawa: 46 dni', 'zwroty: wszystkie'] },
];
function cardHTML(c, x, rot, sc, stamp, stampA, extra = '') {
  let inner;
  if (c === 'G') {
    const lt0 = extra.lt || 0;
    inner = `<div class="abs" style="left:0;top:0;width:940px;height:1180px;background:${GRAD}"></div>
     <div class="abs" style="left:0;top:0;width:940px;height:1180px;background:radial-gradient(circle at 50% 30%,rgba(255,255,255,.35),transparent 60%)"></div>
     <div class="abs" style="left:0;top:${170}px;width:940px;text-align:center"><img src="logo_black.png" style="width:${640 * (1 + 0.03 * Math.sin(lt0 * 3))}px"></div>`;
    const tags = ['podcast', 'rolki', 'wywiady', 'kurs online', '2 h · 300 zł'];
    let tg = ''; tags.forEach((t, i) => { const q = lt0 - 0.35 - i * 0.16; if (q > 0) tg += `<span class="tag" style="transform:scale(${oB(q / .25, 2)});${i === 4 ? 'background:#000' : 'background:rgba(0,0,0,.22)'}">${t}</span>`; });
    inner += `<div class="abs" style="left:50px;bottom:60px;width:850px">
      <div style="display:flex;align-items:center;gap:20px"><span style="font-family:IDB;font-size:92px;color:#fff">Gadka studio</span><span style="width:46px;height:46px;border-radius:23px;background:#2D8CFF;color:#fff;display:flex;align-items:center;justify-content:center;font:900 30px Inter">✓</span></div>
      <div style="font:700 40px Inter;color:#fff;margin:6px 0 6px">początek Twojej marki osobistej</div>
      <div style="font:600 32px Inter;color:#fff;opacity:.85;margin:0 0 24px">📍 Warszawa · ambitny wybór, mała cena</div>${tg}</div>`;
  } else {
    inner = `<div class="abs" style="left:0;top:0;width:940px;height:1180px;background:${c.bg}"></div>
     <div class="abs" style="left:0;top:180px;width:940px;text-align:center;font-size:420px;filter:drop-shadow(0 30px 40px rgba(0,0,0,.3))">${c.e}</div>
     <div class="abs" style="left:0;top:0;width:940px;height:1180px;background:linear-gradient(transparent 50%,rgba(0,0,0,.6))"></div>
     <div class="abs" style="left:50px;bottom:60px;width:850px">
      <div style="font-family:IDB;font-size:72px;color:#fff;line-height:1.05">${c.name}${c.age ? `, <span style="font-family:Inter;font-weight:500">${c.age}</span>` : ''}</div>
      <div style="font:600 34px Inter;color:#fff;opacity:.85;margin:12px 0 22px">📍 ${c.km}</div>
      ${c.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>`;
  }
  let st = '';
  if (stamp === 'no' && stampA > 0) st = `<div class="stamp" style="right:60px;color:${NO};border-color:${NO};transform:rotate(18deg) scale(${0.7 + 0.3 * oB(stampA, 2)});opacity:${cl(stampA * 3)}">NOPE</div>`;
  if (stamp === 'yes' && stampA > 0) st = `<div class="stamp" style="left:60px;color:${YES};border-color:${YES};transform:rotate(-18deg) scale(${0.7 + 0.3 * oB(stampA, 2)});opacity:${cl(stampA * 3)}">LIKE</div>`;
  return `<div class="card" style="transform:translateX(${x}px) rotate(${rot}deg) scale(${sc})">${inner}${st}</div>`;
}
function buttons(t, pressNo, pressYes) {
  const sN = 1 - 0.15 * Math.sin(Math.PI * cl(pressNo)), sY = 1 - 0.15 * Math.sin(Math.PI * cl(pressYes));
  return `<div class="btn" style="left:270px;background:#2A1A28;border:5px solid ${NO};color:${NO};transform:scale(${sN})">✕</div>
          <div class="btn" style="left:640px;background:${GRAD};color:#fff;transform:scale(${sY})">♥</div>`;
}
function header(t) {
  const k = oB((t - 0.05) / 0.35, 2);
  return `<div class="stk" style="top:150px;transform:scale(${0.6 + 0.4 * k});opacity:${cl(t / .15)}"><span style="font-family:IDB;font-size:66px;color:${CR};line-height:1.1;white-space:normal;display:inline-block;width:960px">Szukasz pomysłu<br>na siebie <span style="background:${GRAD};-webkit-background-clip:text;color:transparent">w internecie?</span></span></div>`;
}
function sceneSwipe(t) {
  let h = header(t);
  const NT = D.NOPE;  // czasy odrzuceń
  let idx = NT.filter(x => t >= x + 0.32).length;   // ile już odleciało
  // karta pod spodem (następna)
  const next = idx + 1;
  if (next <= 4) {
    const prevGone = idx > 0 ? oC((t - NT[idx - 1] - 0.1) / 0.3) : 0;
    const sc = 0.92 + 0.08 * (idx < 4 && t >= NT[idx] ? oC((t - NT[idx]) / 0.32) : 0);
    h += cardHTML(next < 4 ? CARDS[next] : 'G', 0, 0, sc, null, 0, { lt: 0, z: 0 });
  }
  // aktualna karta
  if (idx < 4) {
    const c = CARDS[idx], tn = NT[idx];
    const ent = idx === 0 ? oB((t - 0.25) / 0.45, 1.5) : 1;
    let x = 0, rot = 0, sa = 0;
    if (t >= tn - 0.3) { const d = cl((t - tn + 0.3) / 0.3); x = -90 * oC(d); rot = -4 * oC(d); sa = d; }   // przeciąganie
    if (t >= tn) { const f = iC((t - tn) / 0.32); x = -90 - 1300 * f; rot = -4 - 26 * f; sa = 1; }
    h += cardHTML(c, x, rot, idx === 0 ? 0.85 + 0.15 * ent : 1, 'no', sa);
  } else {
    // karta Gadki: chwila zawahania, potem w prawo
    const lt = t - (NT[3] + 0.32), ty = D.YES;
    let x = Math.sin(lt * 3) * 8, rot = 0, sa = 0;
    if (t >= ty - 0.3) { const d = cl((t - ty + 0.3) / 0.3); x = 90 * oC(d); rot = 4 * oC(d); sa = d; }
    if (t >= ty) { const f = iC((t - ty) / 0.35); x = 90 + 1300 * f; rot = 4 + 26 * f; sa = 1; }
    h += cardHTML('G', x, rot, 1, 'yes', sa, { lt, z: cl(lt / 2) });
  }
  const pn = NT.map(x => (t - x + 0.12) / 0.25).find(v => v > 0 && v < 1) || 0;
  const py = (t - D.YES + 0.12) / 0.25;
  h += buttons(t, pn, py > 0 && py < 1 ? py : 0);
  // palec przy decyzji o Gadce
  if (idx >= 4 && t < D.YES + 0.2) {
    const m = oC((t - D.YES + 0.9) / 0.6);
    h += `<div class="abs" style="left:${960 - 230 * m}px;top:${1900 - 250 * m}px;font-size:140px;transform:scale(${t >= D.YES - 0.12 && t < D.YES + 0.05 ? .85 : 1})">👆</div>`;
  }
  return h;
}
function sceneMatch(t) {
  const lt = t - D.MATCH;
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${GRAD};opacity:${cl(lt / .2)}"></div>`;
  // serca w tle
  for (let i = 0; i < 26; i++) {
    const sp = 0.5 + hash(i, 1), x = hash(i, 2) * 1080, y = 1950 - ((lt * 520 * sp + hash(i, 3) * 1900) % 2100);
    h += `<div class="abs" style="left:${x}px;top:${y}px;font-size:${50 + 70 * hash(i, 4)}px;opacity:.35;color:#fff;transform:rotate(${(hash(i, 5) - .5) * 40}deg)">♥</div>`;
  }
  const k = oB(lt / 0.45, 2.2);
  h += `<div class="stk" style="top:420px;transform:scale(${0.4 + 0.6 * k}) rotate(-4deg)"><span style="font-family:IDBI;font-size:150px;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,.25)">To jest</span></div>`;
  h += `<div class="stk" style="top:570px;transform:scale(${0.4 + 0.6 * oB((lt - .12) / .45, 2.4)}) rotate(-4deg)"><span style="font-family:IDBI;font-size:230px;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,.25)">match!</span></div>`;
  // dwa awatary
  const a = oC((lt - 0.3) / 0.45);
  h += `<div class="abs" style="left:${300 - 260 * (1 - a)}px;top:960px;width:300px;height:300px;border-radius:150px;border:10px solid #fff;background:#2A1A28;display:flex;align-items:center;justify-content:center;font-size:150px;transform:rotate(-8deg)">🎙️</div>`;
  h += `<div class="abs" style="left:${480 + 260 * (1 - a)}px;top:960px;width:300px;height:300px;border-radius:150px;border:10px solid #fff;overflow:hidden;transform:rotate(8deg);background:${OR};display:flex;align-items:center;justify-content:center"><img src="logo_black.png" style="width:240px"></div>`;
  if (lt > 0.7) h += `<div class="stk" style="top:1360px;opacity:${cl((lt - .7) / .2)};font:600 46px Inter;color:#fff">Ty i Gadka studio polubiliście się nawzajem</div>`;
  if (lt > 1.0) h += `<div class="stk" style="top:1480px;transform:scale(${oB((lt - 1) / .3)})"><span style="display:inline-block;background:#fff;color:${PK};font:800 48px Inter;padding:30px 70px;border-radius:60px">Napisz wiadomość</span></div>`;
  if (lt < 0.1) h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:#fff;opacity:${1 - lt / .1}"></div>`;
  return h;
}
function bubble(side, text, k, y) {
  const r = side === 'r';
  return `<div class="abs" style="${r ? 'right' : 'left'}:60px;top:${y}px;max-width:780px;padding:30px 40px;border-radius:44px;${r ? 'border-bottom-right-radius:12px' : 'border-bottom-left-radius:12px'};
    background:${r ? GRAD : '#2E1E2C'};color:#fff;font:500 46px/1.3 Inter;transform:scale(${0.6 + 0.4 * oB(k, 2)});transform-origin:${r ? '100%' : '0'} 100%;opacity:${cl(k * 3)}">${text}</div>`;
}
function sceneChat(t) {
  const lt = t - D.CHAT;
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${BG}"></div>`;
  h += `<div class="abs" style="left:0;top:0;width:1080px;height:330px;background:#24141F;border-bottom:2px solid #3a2636"></div>
    <div class="abs" style="left:60px;top:180px;width:110px;height:110px;border-radius:55px;overflow:hidden;background:${OR};display:flex;align-items:center;justify-content:center"><img src="logo_black.png" style="width:90px"></div>
    <div class="abs" style="left:200px;top:186px;font:800 46px Inter;color:#fff">Gadka studio</div>
    <div class="abs" style="left:200px;top:246px;font:500 32px Inter;color:${YES}">● aktywne teraz</div>`;
  const M = D.MSG;
  const msgs = [['l', 'Hej 👋 Zacznijmy Twoją markę. 2 h w studiu za 300 zł, kamery i mikrofony w cenie.'], ['r', 'Podcast i kilka rolek za jednym razem? Sobota 10:00?'], ['l', 'Zarezerwowane ✅ Do zobaczenia przy mikrofonie 🎙️']];
  let y = 420;
  msgs.forEach((m, i) => {
    if (lt >= M[i] - D.CHAT) { h += bubble(m[0], m[1], (lt - (M[i] - D.CHAT)) / 0.3, y); y += m[1].length > 40 ? 260 : 170; }
    else if (i === msgs.length - 1 || lt >= M[i] - D.CHAT - 0.6) {
      if (lt >= M[i] - D.CHAT - 0.6 && m[0] === 'l') {
        const dots = [0, 1, 2].map(j => `<span style="display:inline-block;width:22px;height:22px;border-radius:11px;background:#fff;margin:0 6px;opacity:${0.3 + 0.7 * (0.5 + 0.5 * Math.sin(lt * 12 - j))}"></span>`).join('');
        h += `<div class="abs" style="left:60px;top:${y}px;padding:30px 36px;border-radius:44px;background:#2E1E2C">${dots}</div>`;
      }
    }
  });
  return h;
}
function sceneEnd(t) {
  const lt = t - D.END;
  const R = 2300 * oC(lt / 0.5);
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:${BG}"></div><div class="abs" style="left:${540 - R}px;top:${1700 - R}px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;background:${GRAD}"></div>`;
  if (lt > 0.25) h += `<div class="stk" style="top:470px;transform:scale(${0.4 + 0.6 * oB((lt - .25) / .4, 2.2)})"><img src="logo_black.png" style="width:760px"></div>`;
  if (lt > 0.5) h += `<div class="stk" style="top:860px;transform:scale(${0.6 + 0.4 * oB((lt - .5) / .3)}) rotate(-2deg)"><span style="display:inline-block;background:#000;color:#fff;font-family:IDB;font-size:88px;padding:30px 56px;border-radius:100px">gadkastudio.pl</span></div>`;
  if (lt > 0.8) h += `<div class="stk" style="top:1080px;opacity:${cl((lt - .8) / .25)};font-family:PopB;font-size:48px;color:#000">Warszawa · 2 h od 300 zł · sprzęt w cenie</div>`;
  if (lt > 1.05) h += `<div class="stk" style="top:1230px;opacity:${cl((lt - 1.05) / .25)};transform:translateY(${(1 - oC((lt - 1.05) / .3)) * 30}px)"><span style="display:inline-block;background:#fff;color:#000;font-family:IDBI;font-size:62px;padding:18px 36px;transform:rotate(-3deg)">Marka osobista od 300 zł ♥</span></div>`;
  return h;
}
window.renderAt = function (t) {
  stage.style.transform = '';
  let h = `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:radial-gradient(ellipse at 50% 40%,#2C1528,${BG})"></div>`;
  if (t < D.MATCH) h += sceneSwipe(t);
  else if (t < D.CHAT) h = sceneMatch(t);
  else if (t < D.END) h = sceneChat(t);
  else h = sceneEnd(t);
  h += `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;pointer-events:none;opacity:.06;mix-blend-mode:overlay;background-image:url(img/noise.png);background-position:${(hash(Math.floor(t * 30), 9) * 400) | 0}px ${(hash(Math.floor(t * 30), 8) * 400) | 0}px"></div>`;
  stage.innerHTML = h;
  return true;
};
document.fonts.ready.then(() => setTimeout(() => window.READY = true, 400));
