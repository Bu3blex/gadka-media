// ---- montaż (od dropu): [typ, liczba uderzeń]
const CUTS = [['mic', 2], ['cam', 2], ['light', 2], ['w', 1, OR, BK, 'ZERO'], ['w', 1, BK, OR, 'WYMÓWEK.'], ['four', 2], ['files', 1], ['w', 1, CR, BK, '2 H = 300 ZŁ'], ['rec', 2]];
function cutAt(lt) {
  let b = 0;
  for (let i = 0; i < CUTS.length; i++) { const d = CUTS[i][1] * D.BEAT; if (lt < b + d || i === CUTS.length - 1) return [i, lt - b, d]; b += d; }
}
const full = (inner, css = '') => `<div class="abs" style="left:0;top:0;width:1080px;height:1920px;overflow:hidden;${css}">${inner}</div>`;
function photoFill(code, fx, scale, extraCss = '', tx = 0) {
  return `<img src="img/${code}.jpg" style="position:absolute;height:1920px;left:50%;top:0;transform:translateX(calc(-${fx * 100}% + ${tx}px)) scale(${scale});transform-origin:${fx * 100}% 50%;${extraCss}">`;
}
function hudCorners(col = '#fff', m = 90, L = 120, w = 7, top = 260, bot = 1560) {
  return `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><g stroke="${col}" stroke-width="${w}" fill="none">
   <path d="M${m} ${top + L} V${top} H${m + L}"/><path d="M${1080 - m - L} ${top} H${1080 - m} V${top + L}"/>
   <path d="M${m} ${bot - L} V${bot} H${m + L}"/><path d="M${1080 - m - L} ${bot} H${1080 - m} V${bot - L}"/></g></svg>`;
}
function sceneMontage(t) {
  const lt = t - D.DROP; const [k, ct, dur] = cutAt(lt); const c = CUTS[k]; const p = ct / dur;
  let h = '';
  const sx = (hash(k, Math.floor(t * 60)) - .5) * 24 * (1 - cl(ct / .14));
  stage.style.transform = `translate(${sx}px,0)`;
  const bt = D.BEAT;
  if (c[0] === 'mic') {
    // zbliżenie produktowe: powolny najazd, reflektor, przejście światła, licznik ×1..×4
    h += full(photoFill('056', .52, 1.32 - 0.12 * oC(p), 'filter:contrast(1.15) saturate(1.1) brightness(1.05)', -60 * p));
    h += full('', `background:radial-gradient(ellipse 70% 45% at 52% 48%, rgba(0,0,0,0) 0%, rgba(0,0,0,.55) 70%, rgba(0,0,0,.85) 100%)`);
    const sw = cl((ct - 0.15) / 0.6);
    if (sw > 0 && sw < 1) h += full('', `background:linear-gradient(110deg,transparent ${sw * 180 - 60}%,rgba(255,220,190,.35) ${sw * 180 - 45}%,transparent ${sw * 180 - 30}%);mix-blend-mode:screen`);
    const n = Math.min(4, 1 + Math.floor(ct / (bt / 2)));
    const pop = oB((ct % (bt / 2)) / 0.18, 2.4);
    h += `<div class="abs" style="left:80px;top:1250px;font-family:PopB;font-size:40px;letter-spacing:10px;color:${OR};opacity:${cl(ct / .15)}">MIKROFONY</div>`;
    h += `<div class="abs" style="left:76px;top:1310px;font-family:IDB;font-size:150px;color:${CR};line-height:1;transform:translateX(${(1 - oC(ct / .3)) * -80}px);opacity:${cl(ct / .12)}">Shure SM7B</div>`;
    h += `<div class="abs" style="left:76px;top:1480px;font-family:IDB;font-size:210px;line-height:1;color:transparent;-webkit-text-stroke:5px ${OR};transform:scale(${0.6 + 0.4 * pop});transform-origin:0 50%">×${n}</div>`;
    h += `<div class="abs" style="left:330px;top:1560px;font-family:PopM;font-size:38px;color:${CR};opacity:${cl((ct - .4) / .2)}">po jednym dla każdego</div>`;
    // linia wskazująca
    const L = 300 * oC((ct - .2) / .35);
    h += `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><path d="M560 1240 L560 ${1240 - L}" stroke="${CR}" stroke-width="4"/><circle cx="560" cy="${1240 - L}" r="${L > 5 ? 14 : 0}" fill="${OR}"/></svg>`;
  } else if (c[0] === 'cam') {
    // widok przez wizjer kamery: ostrzenie, blokada AF, REC, parametry
    const focus = cl(ct / 0.45);
    h += full(photoFill('101', .3, 1.12 - 0.05 * p, `filter:blur(${(1 - oC(focus)) * 14}px) contrast(1.1) saturate(1.1)`));
    h += full('', 'background:linear-gradient(rgba(0,0,0,.35),rgba(0,0,0,0) 25%,rgba(0,0,0,0) 70%,rgba(0,0,0,.6))');
    // siatka trójpodziału
    h += `<svg class="abs" style="left:0;top:0;opacity:.35" width="1080" height="1920"><g stroke="#fff" stroke-width="2"><path d="M360 0V1920M720 0V1920M0 640H1080M0 1280H1080"/></g></svg>`;
    h += hudCorners('#fff');
    // ramka AF
    const afs = 420 - 180 * oC(focus), locked = focus >= 1, col = locked ? '#3CFF7A' : '#fff';
    h += `<div class="abs" style="left:${560 - afs / 2}px;top:${900 - afs / 2}px;width:${afs}px;height:${afs}px;border:5px solid ${col};opacity:${locked && Math.floor(ct * 12) % 2 && ct < .7 ? .4 : 1}"></div>`;
    const recOn = Math.floor(ct * 3) % 2 === 0;
    h += `<div class="abs" style="left:110px;top:290px;display:flex;align-items:center;gap:16px;font:700 44px Inter;color:#fff"><span style="width:34px;height:34px;border-radius:17px;background:${recOn ? '#FF2A2A' : 'transparent'};box-shadow:0 0 30px #f22"></span>REC</div>`;
    h += `<div class="abs" style="right:110px;top:292px;font:700 42px Inter;color:#fff;text-align:right">4K · 30p</div>`;
    h += `<div class="abs" style="left:0;width:1080px;top:1470px;display:flex;justify-content:center;gap:56px;font:600 36px Inter;color:#fff;opacity:.9"><span>ISO 800</span><span>1/60</span><span>f/2.8</span><span>WB 3200K</span></div>`;
    const k2 = oB((ct - 0.45) / 0.3, 2.2);
    if (ct > 0.45) h += `<div class="stk" style="top:1150px;transform:scale(${0.6 + 0.4 * k2}) rotate(-3deg)"><span class="mk" style="font-size:112px;box-shadow:10px 10px 0 #000">2× SONY 4K</span></div>`;
  } else if (c[0] === 'light') {
    // to samo ujęcie, kolor światła zmienia się w rytm
    const step = Math.floor(ct / (bt / 2)); const hues = [0, 150, 230, 300][step % 4];
    const flashk = 1 - cl((ct % (bt / 2)) / 0.1);
    h += full(photoFill('104', .5, 1.1 - 0.05 * p, `filter:hue-rotate(${hues}deg) saturate(1.5) contrast(1.1) brightness(${1 + 0.25 * flashk})`));
    h += full('', 'background:linear-gradient(rgba(0,0,0,.4),rgba(0,0,0,0) 30%,rgba(0,0,0,0) 60%,rgba(0,0,0,.75))');
    const sw = ['#53FF6A', '#2AD8FF', '#7A5CFF', '#FF4FD8'];
    h += `<div class="abs" style="left:0;width:1080px;top:1260px;text-align:center;font-family:PopB;font-size:40px;letter-spacing:10px;color:${CR}">PROFESJONALNE</div>`;
    h += `<div class="stk" style="top:1320px;font-family:IDB;font-size:170px;color:${CR};line-height:1;transform:scale(${1 + 0.06 * flashk})">ŚWIATŁO</div>`;
    h += `<div class="abs" style="left:0;width:1080px;top:1530px;display:flex;justify-content:center;gap:30px">` +
      sw.map((s, i) => `<span style="width:${i === step % 4 ? 84 : 56}px;height:${i === step % 4 ? 84 : 56}px;border-radius:50%;background:${s};box-shadow:0 0 ${i === step % 4 ? 50 : 0}px ${s};border:5px solid ${i === step % 4 ? '#fff' : 'transparent'}"></span>`).join('') + `</div>`;
  } else if (c[0] === 'w') {
    const s = 1 + 0.9 * (1 - oE(ct / 0.2));
    h += full('', `background:${c[2]}`);
    const fs = c[4].length > 5 ? 150 : 300;
    h += `<div class="stk" style="top:${960 - fs * 0.55}px;font-family:IDB;font-size:${fs}px;color:${c[3]};transform:scale(${s});letter-spacing:-4px">${c[4]}</div>`;
  } else if (c[0] === 'four') {
    // 2x2 miejsca, numery wskakują po kolei
    const tiles = [['028', .55], ['010', .5], ['019', .3], ['001', .5]];
    const g = 10, tw = (1080 - g) / 2, th = (1920 - g) / 2;
    tiles.forEach(([code, fx], i) => {
      const ti = i * (bt / 2) * 0.9; const q = (ct - ti) / 0.22;
      if (q < 0) return;
      const x = (i % 2) * (tw + g), y = Math.floor(i / 2) * (th + g);
      h += `<div class="abs" style="left:${x}px;top:${y}px;width:${tw}px;height:${th}px;overflow:hidden;opacity:${cl(q * 3)}">
        <img src="img/${code}.jpg" style="position:absolute;height:${th}px;left:50%;transform:translateX(-${fx * 100}%) scale(${1.25 - 0.2 * oC(q)});transform-origin:${fx * 100}% 50%;filter:contrast(1.1) saturate(1.1)"></div>`;
      h += `<div class="abs" style="left:${x + tw / 2 - 70}px;top:${y + th / 2 - 70}px;width:140px;height:140px;border-radius:70px;background:${OR};color:#000;font:900 88px IDB;display:flex;align-items:center;justify-content:center;transform:scale(${oB(q, 2.6)});box-shadow:0 10px 40px rgba(0,0,0,.4)">${i + 1}</div>`;
    });
    if (ct > 4 * (bt / 2) * 0.9 - 0.05) {
      const q = oB((ct - 4 * (bt / 2) * 0.9 + 0.05) / 0.25, 2.4);
      h += `<div class="stk" style="top:870px;transform:scale(${0.5 + 0.5 * q}) rotate(-4deg)"><span class="mk" style="font-size:130px;box-shadow:10px 10px 0 #000">DO 4 OSÓB</span></div>`;
    }
  } else if (c[0] === 'files') {
    h += full(photoFill('050', .42, 1.16 - 0.16 * oE(ct / 0.22), 'filter:contrast(1.12) saturate(1.2)'));
    h += full('', 'background:linear-gradient(transparent 50%,rgba(0,0,0,.6))');
    const s = oB(ct / 0.2, 2.4);
    h += `<div class="stk" style="top:1060px;transform:rotate(-4deg) scale(${0.5 + 0.5 * s})"><span class="mk" style="font-size:118px;background:${CR};box-shadow:10px 10px 0 #000">PLIKI OD RĘKI</span></div>`;
  } else if (c[0] === 'rec') {
    // ekran nagrywania: REC, licznik, poziomy audio, przebieg
    h += full(photoFill('059', .62, 1.15 - 0.08 * p, 'filter:contrast(1.15) saturate(1.1) brightness(.85)'));
    h += full('', 'background:radial-gradient(ellipse 80% 60% at 50% 45%,rgba(0,0,0,0),rgba(0,0,0,.7))');
    h += hudCorners('#fff');
    const pulse = 0.5 + 0.5 * Math.sin(ct * 10);
    h += `<div class="abs" style="left:110px;top:290px;display:flex;align-items:center;gap:18px;font:800 52px Inter;color:#fff"><span style="width:44px;height:44px;border-radius:22px;background:#FF2A2A;box-shadow:0 0 ${20 + 40 * pulse}px #f22"></span>REC</div>`;
    const sec = ct, ss = Math.floor(sec), ff = Math.floor((sec % 1) * 30);
    h += `<div class="abs" style="right:110px;top:294px;font:700 48px Inter;color:#fff">00:00:0${ss}:${String(ff).padStart(2, '0')}</div>`;
    // poziomy audio (4 kanały)
    for (let ch = 0; ch < 4; ch++) {
      const lv = 0.35 + 0.6 * Math.abs(Math.sin(ct * 13 + ch * 1.7)) * (0.6 + 0.4 * (1 - cl((ct % bt) / bt)));
      for (let s2 = 0; s2 < 16; s2++) {
        const on = s2 / 16 < lv, col = s2 > 12 ? '#FF2A2A' : (s2 > 9 ? '#FFC23A' : '#3CFF7A');
        h += `<div class="abs" style="left:${930 + ch * 26}px;top:${1300 - s2 * 30}px;width:18px;height:22px;background:${on ? col : 'rgba(255,255,255,.15)'}"></div>`;
      }
    }
    h += `<div class="abs" style="left:925px;top:1330px;font:600 24px Inter;color:#fff;opacity:.8">CH 1–4</div>`;
    // przebieg
    let path = 'M80 1700';
    for (let x = 0; x <= 920; x += 8) { const a = Math.sin(x * 0.045 + ct * 18) * Math.sin(x * 0.011 + ct * 3) * 70 * (0.5 + 0.5 * Math.abs(Math.sin(x * 0.02 + ct * 5))); path += ` L${80 + x} ${1700 + a}`; }
    h += `<svg class="abs" style="left:0;top:0" width="1080" height="1920"><path d="${path}" stroke="${OR}" stroke-width="6" fill="none"/></svg>`;
    const q = oB(ct / 0.25, 2.2);
    h += `<div class="stk" style="top:1420px;font-family:IDB;font-size:150px;color:${CR};transform:scale(${0.6 + 0.4 * q})">NAGRYWASZ.</div>`;
  }
  // logo
  const darkTile = c[0] === 'w' && c[2] !== BK;
  if (c[0] !== 'four') h += `<img class="abs" src="${darkTile ? 'logo_black.png' : 'logo.png'}" style="left:440px;top:150px;width:200px">`;
  if (ct < 0.07) h += full('', `background:#fff;opacity:${0.7 * (1 - ct / .07)}`);
  return h;
}
