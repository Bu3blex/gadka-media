"""Rolki Gadka studio v3: kinetyczna typografia, szybkie cięcia w rytm, zoom-punch, liczniki, czat, przekreślenia.
Dźwięk: syntetyczny beat 120 BPM + whoosh na cięciach + pop przy wejściu napisów.
Cięcia najlepiej co 0,5 s (jedno uderzenie)."""
import os, sys, math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kreatywne import *

FPS = 30
W, H = 1080, 1920
BPM = 120
BEAT = 60 / BPM
SAFE_TOP, SAFE_BOT = 260, 1420   # treść w strefie wolnej od UI Instagrama


def ease_out(t): return 1 - (1 - min(max(t, 0), 1)) ** 3


def ease_back(t, s=2.2):
    t = min(max(t, 0), 1) - 1
    return 1 + t * t * ((s + 1) * t + s)


def scaled(lay, k):
    if abs(k - 1) < 0.004:
        return lay
    return lay.resize((max(1, round(lay.width * k)), max(1, round(lay.height * k))), Image.BILINEAR)


def comp(fr, lay, cx, cy, k=1.0, alpha=1.0):
    l = scaled(lay, k)
    if alpha < 1:
        l = l.copy(); l.putalpha(l.getchannel("A").point(lambda v: round(v * alpha)))
    fr.paste(l, (round(cx - l.width / 2), round(cy - l.height / 2)), l)


def line_layer(t, size, fill=CREAM, it=False, outline=None, bg=None):
    f = FX(size, it); c = cap(f)
    w_ = round(tw(f, t)) + 40; h_ = round(c * 1.5) + 20
    lay = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if outline:
        d.text((20, 10 + c * 1.18), t, font=f, fill=(0, 0, 0, 0), anchor="ls", stroke_width=7, stroke_fill=outline)
    else:
        d.text((20, 10 + c * 1.18), t, font=f, fill=fill, anchor="ls")
    return lay


def logo_layer(width, color=None):
    return logo_img(width, color)


def with_logo(fr, bg_dark=True, width=200):
    lg = logo_img(width, None if bg_dark else BLACK)
    fr.paste(lg, (round(W / 2 - width / 2), 130), lg)
    return fr


# ================================================================ UJĘCIA
def k_words(lines, dur, bg=BLACK, fg=CREAM, it=False, step=None, size=None, start=0.0):
    """słowa/wiersze wskakują po kolei z odbiciem; linia: 'tekst' | ('tekst', kolor) | ('tekst', 'o', kolor_obrysu)"""
    specs = [(l, fg, None) if not isinstance(l, tuple) else (l[0], l[1], l[2] if len(l) > 2 else None) for l in lines]
    s = size or fit([sp[0] for sp in specs], W - 140, 230, it)
    lays = [line_layer(t, s, col if col != "o" else None, it, outline=o if col == "o" else None) for t, col, o in specs]
    c = cap(FX(s, it)); stepy = c * 1.32
    total = c + (len(lays) - 1) * stepy
    y0 = (SAFE_TOP + SAFE_BOT) / 2 - total / 2
    st = step or min(0.18, (dur - 0.3) / max(1, len(lays)))
    pops = [start + i * st for i in range(len(lays))]
    dark = not (is_light(bg) or bg == ORANGE)

    def fn(t, fr=None):
        fr = Image.new("RGB", (W, H), bg)
        with_logo(fr, dark)
        for i, lay in enumerate(lays):
            lt = t - pops[i]
            if lt < 0: continue
            k = 0.55 + 0.45 * ease_back(lt / 0.22)
            comp(fr, lay, W / 2, y0 + i * stepy + c / 2 + 8, k)
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


def k_photo(code, dur, lines=None, stick=None, emo=None, duo=False, fx=None, msize=104, mbg=ORANGE, mfg=BLACK, pos=0.62, zoom_in=True, angle=-3):
    """zdjęcie na pełny kadr: uderzenie zoomem, krótki shake, napis na zakreślaczu, naklejka"""
    big = cover(code, round(W * 1.22), round(H * 1.22), fx=fx)
    if duo: big = duotone(big)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = np.zeros((H, 1), np.float32)
    ys = np.arange(H)
    g[:, 0] = np.clip((ys - H * 0.35) / (H * 0.45), 0, 1) ** 1.4 * 200 + np.clip((260 - ys) / 260, 0, 1) * 150
    ov.putalpha(Image.fromarray(g.astype(np.uint8)).resize((W, H)))
    mk = marker(lines, msize, bg=mbg, fg=mfg, angle=angle) if lines else None
    stl = sticker(stick, 52, bg=CREAM, fg=BLACK, angle=5) if stick else None
    eml = emoji(emo, 170, angle=-12) if emo else None
    rnd = random.Random(hash(code) % 1000)
    shake = [(rnd.randint(-14, 14), rnd.randint(-14, 14)) for _ in range(6)]
    pops = [0.1] + ([0.3] if stl else [])

    def fn(t):
        p = t / dur
        z = (1.20 - 0.14 * ease_out(t / 0.35) - 0.04 * p) if zoom_in else (1.02 + 0.10 * p)
        cw = W * 1.22 / z; ch = H * 1.22 / z
        x0 = (big.width - cw) / 2; y0 = (big.height - ch) / 2
        fi = int(t * FPS)
        if fi < 6:
            x0 += shake[fi][0] * (1 - fi / 6); y0 += shake[fi][1] * (1 - fi / 6)
        fr = big.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
        fr.alpha_composite(ov)
        fr = fr.convert("RGB")
        with_logo(fr, True)
        if mk is not None and t >= 0.1:
            k = 0.6 + 0.4 * ease_back((t - 0.1) / 0.22)
            comp(fr, mk, W / 2, H * pos, k)
        if stl is not None and t >= 0.3:
            e = ease_out((t - 0.3) / 0.25)
            comp(fr, stl, W - stl.width / 2 - 60 + (1 - e) * 600, H * pos - (mk.height / 2 if mk else 0) - stl.height / 2 - 40)
        if eml is not None and t >= 0.35:
            k = ease_back((t - 0.35) / 0.25)
            comp(fr, eml, 190, H * pos - (mk.height / 2 if mk else 0) - 130, max(0.05, k))
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


def k_counter(to, dur, label=None, frm=0, suffix=" zł", bg=ORANGE, fg=BLACK, sub=None, code=None, top=None):
    """licznik: liczba przewija się do wartości i odbija"""
    dark = not (is_light(bg) or bg == ORANGE)
    base = None
    if code:
        base = shade(duotone(cover(code, W, H)), 0, H, 120, 120); dark = True
    f = FX(fit([f"{max(to, frm)}{suffix}"], W - 120, 300))
    lab = line_layer(label, fit([label], W - 160, 120), fg if not code else CREAM) if label else None
    tp = line_layer(top, fit([top], W - 160, 96), fg if not code else CREAM) if top else None
    run = min(dur * 0.65, 1.2)
    pops = [run]

    def fn(t):
        fr = base.copy() if base else Image.new("RGB", (W, H), bg)
        with_logo(fr, dark)
        d = ImageDraw.Draw(fr)
        v = round(frm + (to - frm) * ease_out(t / run))
        k = 1 + 0.12 * math.sin(min(1, max(0, (t - run) / 0.2)) * math.pi)
        lay = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((W / 2, 340), f"{v}{suffix}", font=f, fill=(fg if not code else CREAM), anchor="ms")
        cy = (SAFE_TOP + SAFE_BOT) / 2
        comp(fr, lay, W / 2, cy, k)
        if tp: comp(fr, tp, W / 2, cy - 280, 1)
        if lab: comp(fr, lab, W / 2, cy + 230, 0.6 + 0.4 * ease_back(t / 0.25))
        if sub and t > run:
            body(d, 80, cy + 340, sub, 46, fg if not code else CREAM, W - 160, center=True, weight="b")
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


def k_strike(title, items, final, dur, bg=BLACK):
    """pozycje pojawiają się i zostają przekreślone; na końcu puenta"""
    f = F("b", 84)
    tl = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
    s = fit(title, W - 160, 110)
    mega(ImageDraw.Draw(tl), 80, 20, title, s, CREAM, bg=None)
    th = round(mega_h(title, s)) + 40
    ms = 124
    while ms > 60 and max(tw(FX(ms, True), l) for l in final) + 60 > W - 100:
        ms -= 4
    mk = marker(final, ms, angle=-3)
    n = len(items); step = BEAT
    t_final = 0.25 + n * step + 0.15
    pops = [0.25 + i * step for i in range(n)] + [t_final]

    def fn(t):
        fr = Image.new("RGB", (W, H), bg); with_logo(fr, True)
        fr.paste(tl, (0, SAFE_TOP + 40), tl)
        d = ImageDraw.Draw(fr)
        y = SAFE_TOP + 40 + th + 60
        for i, it_ in enumerate(items):
            lt = t - pops[i]
            if lt < 0: break
            x = 80 - (1 - ease_out(lt / 0.15)) * 80
            d.text((x, y), it_, font=f, fill=MUTED if lt > 0.25 else CREAM)
            if lt > 0.2:
                e = ease_out((lt - 0.2) / 0.2); l = f.getlength(it_)
                mid = y + f.size * 0.62
                d.line((70, mid + 6, 70 + (l + 30) * e, mid + 6 - 12 * e), fill=ORANGE, width=14)
            y += round(f.size * 1.4)
        if t >= t_final:
            comp(fr, mk, W / 2, y + 40 + mk.height / 2, 0.6 + 0.4 * ease_back((t - t_final) / 0.22))
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


def k_chat(msgs, dur, title=None, bg=ORANGE, name="Współprowadzący"):
    """dymki czatu pojawiają się jeden po drugim"""
    n = len(msgs)
    layers = [chat_layer(msgs[:k + 1], w=W - 120, size=54, name=name) for k in range(n)]
    tl = None
    if title:
        s = fit(title, W - 160, 120)
        tl = Image.new("RGBA", (W, round(mega_h(title, s)) + 60), (0, 0, 0, 0))
        mega(ImageDraw.Draw(tl), 80, 20, title, s, BLACK if bg == ORANGE else CREAM, bg=None)
    step = min(0.9, (dur - 0.6) / n)
    pops = [0.15 + i * step for i in range(n)]
    dark = not (is_light(bg) or bg == ORANGE)

    def fn(t):
        fr = Image.new("RGB", (W, H), bg); with_logo(fr, dark)
        y = SAFE_TOP + 20
        if tl: fr.paste(tl, (0, y), tl); y += tl.height + 30
        k = max(0, sum(1 for p in pops if t >= p) - 1)
        lay = layers[k]
        lt = t - pops[k]
        dy = (1 - ease_out(lt / 0.2)) * 40
        fr.paste(lay, (60, round(y + dy)), lay)
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


def k_receipt(hook, rows, total, dur, stamp=None):
    rc = receipt(rows, total, w=860, angle=2)
    s = fit(hook, W - 160, 120)
    hl = Image.new("RGBA", (W, round(mega_h(hook, s)) + 60), (0, 0, 0, 0))
    mega(ImageDraw.Draw(hl), 80, 20, hook, s, CREAM, bg=None, align="c", w=W - 160)
    st = sticker(stamp, 60, angle=-10) if stamp else None
    pops = [0.05] + ([dur * 0.6] if st else [])

    def fn(t):
        fr = Image.new("RGB", (W, H), BLACK); with_logo(fr, True)
        fr.paste(hl, (0, SAFE_TOP), hl)
        ty = SAFE_TOP + hl.height + 20 + rc.height / 2
        yy = ty + (1 - ease_out(t / 0.5)) * 1400
        comp(fr, rc, W / 2, yy)
        if st and t >= dur * 0.6:
            comp(fr, st, W / 2 + 150, ty + rc.height * 0.22, 0.5 + 0.5 * ease_back((t - dur * 0.6) / 0.2))
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


def k_cta(title, dur, sub=None, bg=ORANGE):
    dark = not (is_light(bg) or bg == ORANGE)
    lg = logo_img(640, None if dark else BLACK)
    s = fit(title, W - 160, 120)
    tl = Image.new("RGBA", (W, round(mega_h(title, s)) + 60), (0, 0, 0, 0))
    fg = CREAM if dark else BLACK
    mega(ImageDraw.Draw(tl), 80, 20, title, s, fg, bg=None, align="c", w=W - 160)
    pl = sticker("REZERWACJA: " + SITE.upper(), 50, bg=BLACK if not dark else ORANGE, fg=CREAM if not dark else BLACK, angle=-3, px=40, py=26, radius=60)
    pops = [0.0, 0.35]

    def fn(t):
        fr = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(fr)
        y = 420
        comp(fr, lg, W / 2, y + lg.height / 2, 0.5 + 0.5 * ease_back(t / 0.3))
        y += lg.height + 80
        if t > 0.2:
            fr.paste(tl, (0, round(y + (1 - ease_out((t - 0.2) / 0.25)) * 60)), tl)
        y += tl.height + 10
        if sub and t > 0.3:
            y = body(d, 80, y, sub, 46, fg, W - 160, center=True, weight="m")
        if t > 0.35:
            k = (0.6 + 0.4 * ease_back((t - 0.35) / 0.25)) * (1 + 0.035 * math.sin((t - 0.35) * 2 * math.pi / BEAT))
            comp(fr, pl, W / 2, y + 120, k)
        return fr
    return dict(dur=dur, fn=fn, pops=pops)


# ================================================================ DŹWIĘK
SR = 44100


def _env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def soundtrack(total, cuts, pops, seed=1):
    rng = np.random.default_rng(seed)
    N = int(total * SR) + SR
    L = np.zeros(N);
    def add(sig, at, gain=1.0):
        i = int(at * SR)
        if i >= N: return
        j = min(N, i + len(sig)); L[i:j] += sig[:j - i] * gain
    # kick
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t / 0.035); kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.12)
    # clap/snare
    n2 = int(0.22 * SR); sn = rng.normal(0, 1, n2) * _env(n2, 0.001, 0.06)
    sn = np.convolve(sn, np.ones(6) / 6, "same") - np.convolve(sn, np.ones(40) / 40, "same")
    # hat
    n3 = int(0.06 * SR); hat = rng.normal(0, 1, n3); hat = (hat - np.convolve(hat, np.ones(8) / 8, "same")) * _env(n3, 0.0005, 0.015)
    beats = int(total / BEAT) + 2
    roots = [55.0, 43.65, 65.41, 49.0]   # A1 F1 C2 G1
    for b in range(beats):
        tb = b * BEAT
        add(kick, tb, 0.9)
        if b % 2 == 1: add(sn, tb, 0.45)
        add(hat, tb + BEAT / 2, 0.22); add(hat, tb + BEAT * 0.75, 0.10)
        # bas (offbeat)
        fr_ = roots[(b // 4) % 4]; nb_ = int(BEAT * 0.45 * SR); tt = np.arange(nb_) / SR
        bass = (np.sin(2 * np.pi * fr_ * tt) + 0.3 * np.sin(4 * np.pi * fr_ * tt)) * _env(nb_, 0.005, 0.18)
        add(bass, tb + BEAT / 2, 0.38)
    # whoosh przed cięciem
    nw = int(0.28 * SR); tw_ = np.arange(nw) / SR
    wn = rng.normal(0, 1, nw); wn = wn - np.convolve(wn, np.ones(30) / 30, "same")
    wh = wn * (tw_ / tw_[-1]) ** 2.2 * 0.35
    for c in cuts:
        if c > 0.3: add(wh, c - 0.28, 0.6)
    # pop
    npp = int(0.05 * SR); tp_ = np.arange(npp) / SR
    pop = np.sin(2 * np.pi * (1300 - 9000 * tp_) * tp_) * _env(npp, 0.0005, 0.015)
    for p in pops: add(pop, p, 0.35)
    L = L[:int(total * SR)]
    # fade out
    fo = int(0.4 * SR); L[-fo:] *= np.linspace(1, 0, fo)
    L = np.tanh(L * 1.2); L /= max(1e-6, np.abs(L).max()); L *= 0.85
    return L


# ================================================================ RENDER
def render(shots, path, flash=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    total = sum(s["dur"] for s in shots)
    cuts, pops, t0 = [], [], 0.0
    for s in shots:
        cuts.append(t0); pops += [t0 + p for p in s["pops"]]; t0 += s["dur"]
    wav = path[:-4] + ".wav"
    a = (soundtrack(total, cuts, pops) * 32767).astype(np.int16)
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.repeat(a[:, None], 2, axis=1).tobytes())
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for si, s in enumerate(shots):
        n = round(s["dur"] * FPS)
        for f in range(n):
            fr = s["fn"](f / FPS)
            if flash and si > 0 and f < 3:
                fr = Image.blend(fr, Image.new("RGB", (W, H), CREAM), [0.55, 0.25, 0.08][f])
            p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    os.remove(wav)
    return path


def frames_preview(shots, path, at=0.6):
    """po jednej klatce z każdego ujęcia (do podglądu)"""
    ims = [s["fn"](min(s["dur"] - 0.05, at if s["dur"] > at else s["dur"] * 0.8)).resize((270, 480)) for s in shots]
    sh = Image.new("RGB", (280 * len(ims), 490), "white")
    for i, im in enumerate(ims): sh.paste(im, (i * 280, 0))
    sh.save(path, quality=85)
    return path
