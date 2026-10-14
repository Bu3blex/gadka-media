"""Rolka „koszyk”: dźwięk syntetyczny + render przeglądarki."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_koszyk_v4.mp4")
FPS, SR = 30, 44100
FLY, PANEL = 0.85, 1.35
ADD = [1.85 + i * 0.56 for i in range(9)]
ALARM = ADD[-1] + 0.65
ALBO, DEL = ALARM + 0.95, ALARM + 1.5
GIN = DEL + 0.9
CHK = GIN + 0.45
TAP = CHK + 5 * 0.3 + 0.55
PROOF, PCUT = TAP + 0.9, 0.72
CHEAP = PROOF + 4 * PCUT
END = CHEAP + 3.7
TOTAL = END + 2.7
DATA = dict(FLY=FLY, PANEL=PANEL, ADD=ADD, ALARM=ALARM, ALBO=ALBO, DEL=DEL, GIN=GIN, CHK=CHK, TAP=TAP, PROOF=PROOF, PCUT=PCUT, CHEAP=CHEAP, END=END, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")
rng = np.random.default_rng(5)
L = int(TOTAL * SR) + SR
mix = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0):
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: mix[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def bell(f, d=0.9, g=1.0, parts=((1, .5, .5), (2.01, .25, .3), (3.0, .12, .2), (4.2, .07, .12))):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in parts) * np.minimum(1, t / .002) * g
def kick(g=1.0):
    t = tt(0.35); f = 50 + 110 * np.exp(-t / 0.03)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.35, 0.001, 0.14) * 2) * g
def hat(d=0.04, g=1.0): t = tt(d); return hp(rng.normal(0, 1, len(t)), 3) * env(d, 0.0005, d / 3) * g
def clap(g=1.0):
    out = np.zeros(int(0.22 * SR))
    for o in (0, 0.011, 0.022):
        s = hp(rng.normal(0, 1, int(0.18 * SR)), 4) * env(0.18, 0.001, 0.04 if o < .02 else 0.08); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.45 * g
def pluck(f, d=0.25, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(d, 0.002, 0.07) * g
def bass(f, d=0.2, g=1.0):
    t = tt(d); return np.tanh(np.sin(2 * np.pi * f * t) * 2) * env(d, 0.003, 0.09) * g
def whoosh(d=0.14, g=1.0):
    n = int(d * SR); return hp(rng.normal(0, 1, n), 4) * np.linspace(0, 1, n) ** 2 * g

def groove(t0, t1, bpm=120, g=1.0, drums=True, filt=1.0):
    """deep house: akordy m7 z pompowaniem, sub-bas, stopa 4/4, klaśnięcie 2/4, otwarty hi-hat na offbeat, shaker"""
    B = 60 / bpm; bar = 4 * B
    chords = [[220.0, 261.63, 329.63, 392.0], [174.61, 220.0, 261.63, 329.63], [261.63, 329.63, 392.0, 493.88], [196.0, 246.94, 293.66, 369.99]]
    roots = [55.0, 43.65, 65.41, 49.0]
    n = int((t1 - t0) * SR); tt_ = np.arange(n) / SR
    pad = np.zeros(n)
    for ci in range(int((t1 - t0) / bar) + 1):
        a, b = int(ci * bar * SR), min(n, int((ci + 1) * bar * SR))
        if a >= n: break
        tl = tt_[a:b] - ci * bar
        for f in chords[ci % 4]:
            for det in (0.997, 1.003):
                for h in range(1, 7):
                    pad[a:b] += np.sin(2 * np.pi * f * det * h * tl) / h * (0.55 ** (h - 1))
        pad[a:b] *= np.minimum(1, tl / 0.08)
    k = max(2, int(60 / filt)); pad = np.convolve(pad, np.ones(k) / k, "same")
    # pompowanie pod stopę
    sc = np.ones(n)
    for q in range(int((t1 - t0) / B) + 1):
        i = int(q * B * SR)
        if i >= n: break
        m = min(n - i, int(B * SR)); sc[i:i + m] = 1 - 0.75 * np.exp(-np.arange(m) / SR / 0.11)
    pad = pad / (np.abs(pad).max() + 1e-9) * 0.22 * sc
    add(pad * g, t0)
    # sub-bas
    for q in range(int((t1 - t0) / B)):
        x = t0 + q * B; r = roots[int(q * B / bar) % 4]
        if drums:
            t = tt(B * 0.9); add(np.sin(2 * np.pi * r * t) * np.minimum(1, t / .01) * np.exp(-t / 0.35) * 0.55 * g * (1 - 0.7 * np.exp(-t / 0.06)), x + B * 0.5)
    if not drums: return
    for q in range(int((t1 - t0) / B)):
        x = t0 + q * B
        add(kick(0.95 * g), x)
        if q % 2 == 1: add(clap(0.8 * g), x)
        oh = hp(rng.normal(0, 1, int(0.18 * SR)), 2) * env(0.18, 0.001, 0.07) * 0.22 * g
        add(oh, x + B / 2)
        for s16 in range(4):
            add(hat(0.02, (0.07 if s16 % 2 == 0 else 0.11) * g), x + s16 * B / 4)

def beat(t0, t1, bpm, g=1.0, melody=True):
    B = 60 / bpm; x = t0; b = 0
    roots = [65.41, 65.41, 87.31, 77.78]       # C2 C2 F2 Eb2
    penta = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
    while x < t1 - 0.05:
        add(kick(0.9 * g), x)
        if b % 2 == 1: add(clap(g), x)
        add(hat(0.035, 0.22 * g), x + B * 0.58); add(hat(0.025, 0.1 * g), x + B * 0.25)
        r = roots[(b // 4) % 4]
        add(bass(r, 0.18, 0.5 * g), x); add(bass(r * 2, 0.12, 0.25 * g), x + B * 0.58)
        if melody:
            n1 = penta[int(rng.integers(0, 6))]; add(pluck(n1, g=0.16 * g), x + B * 0.5)
            if b % 2 == 0: add(pluck(penta[int(rng.integers(0, 6))], g=0.12 * g), x + B * 0.83)
        b += 1; x += B

# ---------- część 1: zakupy
groove(0.0, ADD[0], 120, 0.7, drums=False, filt=0.35)
groove(ADD[0], ALARM, 120, 0.75, filt=0.6)
add(whoosh(0.4, 0.5), FLY - 0.05)
add(whoosh(0.25, 0.35), PANEL - 0.05); add(kick(0.7), PANEL + 0.3)
for i, x in enumerate(ADD[:-1]):
    add(bell(1568 * (1.06 ** i), 0.7, 0.45), x + 0.02)                      # ka-ching
    add(hp(rng.normal(0, 1, int(0.05 * SR)), 2) * env(0.05, 0.0005, 0.015) * 0.5, x)
    for c in range(9): add(hp(rng.normal(0, 1, int(0.006 * SR)), 2) * 0.22, x + 0.05 + c * 0.03)  # licznik
add(pluck(330, 0.4, 0.4), ADD[-1]); add(pluck(311, 0.4, 0.4), ADD[-1] + 0.12)   # „???”
# alarm
for k in range(3):
    t = tt(0.16); add(np.tanh(np.sign(np.sin(2 * np.pi * 196 * t)) * 0.8) * env(0.16, 0.002, 0.2) * 0.35, ALARM + k * 0.2)
# …albo
t = tt(1.2); add(np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t / 0.07)) / SR) * env(1.2, 0.001, 0.5) * 0.9, ALBO)
add(whoosh(0.3, 0.4)[::-1], ALBO + 0.02)
# usuwanie
for i in range(9): add(whoosh(0.12, 0.35), DEL + (8 - i) * 0.075)
t = tt(GIN - DEL); add(np.sin(2 * np.pi * np.cumsum(np.linspace(1100, 180, len(t))) / SR) * np.linspace(0.15, 0.02, len(t)), DEL)
# Gadka: akord
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(bell(f, 1.2, 0.3), GIN + k * 0.07)
for i in range(5): add(pluck(880 * (1.12 ** i), 0.15, 0.3), CHK + i * 0.3)
# narastanie do kliknięcia
d = TAP - (CHK + 1.4); t = tt(d); ramp = (t / d) ** 2
add((lpf(rng.normal(0, 1, len(t)), 6) * 0.6 + np.sin(2 * np.pi * np.cumsum(200 + 700 * ramp) / SR) * 0.2) * ramp, CHK + 1.4)
# klik + sukces + drop
add(hp(rng.normal(0, 1, int(0.02 * SR)), 2) * env(0.02, 0.0003, 0.006) * 0.8, TAP)
for k, f in enumerate([784, 988, 1175, 1568]): add(bell(f, 1.0, 0.28), TAP + 0.08 + k * 0.06)
t = tt(1.3); add(np.sin(2 * np.pi * np.cumsum(42 + 100 * np.exp(-t / 0.08)) / SR) * env(1.3, 0.001, 0.55) * 0.8 + hp(rng.normal(0, 1, len(t)), 3) * env(1.3, 0.001, 0.4) * 0.25, TAP + 0.1)
groove(TAP + 0.1, TOTAL - 0.2, 120, 1.0, filt=1.0)
# dowody
for k in range(4):
    add(whoosh(0.12, 0.3), PROOF + k * PCUT - 0.12)
    add(kick(0.6), PROOF + k * PCUT + 0.1); add(bell(2093, 0.4, 0.15), PROOF + k * PCUT + 0.12)
add(hp(rng.normal(0, 1, int(0.03 * SR)), 2) * env(0.03, 0.0005, 0.008) * 0.6, PROOF + PCUT + 0.36)
# taniej niż
n = int(0.2 * SR); add(hp(rng.normal(0, 1, n), 3) * np.linspace(1, 0.2, n) * 0.4, CHEAP + 0.45)
add(kick(1.1), CHEAP + 0.75); add(bell(1568, 0.6, 0.3), CHEAP + 0.77)
add(kick(0.8), CHEAP + 1.2); add(kick(0.9), CHEAP + 1.35)
add(whoosh(0.3, 0.5), END - 0.3)
m = mix[:int(TOTAL * SR)]
fo = int(0.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.1); m = m / np.abs(m).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))
# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", "8767"], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto("http://127.0.0.1:8767/index.html")
        pg.wait_for_function("window.READY===true", timeout=20000)
        def shot(t):
            pg.evaluate(f"(async()=>{{renderAt({t}); await Promise.all([...document.images].map(i=>i.decode().catch(()=>0)));}})()")
            return pg.screenshot(type="jpeg", quality=93)
        if prev:
            ims = []
            for t in [float(x) for x in prev.split(",")]:
                open(WD + "/_f.jpg", "wb").write(shot(t)); ims.append(Image.open(WD + "/_f.jpg").resize((270, 480)))
            sh = Image.new("RGB", (280 * len(ims), 480), "white")
            for i, m in enumerate(ims): sh.paste(m, (i * 280, 0))
            sh.save(WD + "/prev.jpg"); sys.exit()
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-shortest", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS); t0 = time.time()
        for i in range(n):
            ff.stdin.write(shot(i / FPS))
            if i % 100 == 0: print(i, n, round(time.time() - t0, 1), flush=True)
        ff.stdin.close(); ff.wait()
        print("ok", OUT)
finally:
    srv.terminate()
