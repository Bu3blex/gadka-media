"""Render rolki POV + sound design (wszystko syntetyzowane)."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_pov_v5.mp4")
FPS, SR = 30, 44100

# ---------------- oś czasu
N = [0.10, 0.62, 1.12, 1.58, 2.00, 2.38, 2.70, 2.98, 3.22, 3.42, 3.58, 3.72, 3.84, 3.94]
FREEZE, GADKA, DROP = 4.12, 4.55, 5.40
BEAT = 60 / 128
CUTB = [2, 2, 2, 1, 1, 2, 1, 1, 2]
RECEIPT = DROP + sum(CUTB) * BEAT
ROWT = [RECEIPT + 0.35 + i * 0.2 for i in range(7)]
TOT = ROWT[-1] + 0.3
STAMP = TOT + 0.55
END = STAMP + 1.05
TOTAL = END + 2.3
DATA = dict(N=N, FREEZE=FREEZE, GADKA=GADKA, DROP=DROP, BEAT=BEAT, RECEIPT=RECEIPT, ROWT=ROWT, TOT=TOT, STAMP=STAMP, END=END, TOTAL=TOTAL)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA) + ";")
# ziarno
rng = np.random.default_rng(2)
Image.fromarray((rng.random((600, 600)) * 255).astype(np.uint8)).save(os.path.join(WD, "img", "noise.png"))

# ---------------- dźwięk
L = int(TOTAL * SR) + SR
mixA = np.zeros(L)   # warstwa powiadomień (ucinana na FREEZE)
mixB = np.zeros(L)   # reszta
def tt(d): return np.arange(int(d * SR)) / SR
def add(buf, sig, at, g=1.0):
    i = int(at * SR); j = min(L, i + len(sig))
    if i < L: buf[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def lp(x, a):
    y = np.zeros_like(x); s = 0.0
    aa = np.broadcast_to(a, x.shape)
    for i in range(len(x)): s += aa[i] * (x[i] - s); y[i] = s
    return y
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")

def buzz():
    t = tt(0.24); s = np.sign(np.sin(2 * np.pi * 165 * t)) * 0.5 + np.sin(2 * np.pi * 330 * t) * 0.3
    m = ((t < 0.09) | ((t > 0.13) & (t < 0.22))).astype(float)
    return np.tanh(s * m * 1.5) * 0.5
def blip(i):
    f0 = 900 * (1.045 ** i); out = np.zeros(int(0.32 * SR))
    for k, (f, st, d) in enumerate([(f0, 0, 0.12), (f0 * 1.5, 0.075, 0.22)]):
        t = tt(d); s = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * env(d, 0.002, 0.07)
        i0 = int(st * SR); out[i0:i0 + len(s)] += s
    return out * 0.38
for i, x in enumerate(N):
    add(mixA, buzz(), x, 0.8); add(mixA, blip(i), x + 0.02, 1.0)
# riser
d = FREEZE - 1.7; t = tt(d); nz = rng.normal(0, 1, len(t))
ramp = (t / d) ** 2
ris = lp(nz, 0.02 + 0.5 * ramp) * 0.9 * ramp + np.sin(2 * np.pi * np.cumsum(150 + 900 * ramp) / SR) * 0.18 * ramp
ris += np.sin(2 * np.pi * 45 * t) * 0.3 * ramp
add(mixA, ris, 1.7, 1.0)
mixA[int(FREEZE * SR):] = 0
# scratch + tape stop
t = tt(0.3); car = np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, .1, .2, .3], [1800, 250, 900, 300])) / SR)
scr = hp(rng.normal(0, 1, len(t)), 6) * (0.5 + 0.5 * car) * env(0.3, 0.002, 0.12) * 0.7
tape = np.sin(2 * np.pi * np.cumsum(np.linspace(300, 30, len(t))) / SR) * np.linspace(0.5, 0, len(t))
add(mixB, scr + tape, FREEZE)
# ding Gadki
t = tt(1.6); ding = sum(a * np.sin(2 * np.pi * 1046 * p * t) * np.exp(-t / dc) for p, a, dc in [(1, .5, 1.1), (2, .22, .7), (3, .12, .45), (4.2, .08, .3)])
add(mixB, ding * np.minimum(1, t / 0.003), GADKA, 0.75)
add(mixB, lp(rng.normal(0, 1, int(0.25 * SR)), 0.15) * np.linspace(0, 0.5, int(0.25 * SR)), GADKA - 0.25)
# build: snare roll
def snare(g=1.0, d=0.18):
    t = tt(d); n = hp(rng.normal(0, 1, len(t)), 5) * env(d, 0.001, 0.05)
    return (n + np.sin(2 * np.pi * 190 * t) * env(d, 0.001, 0.03) * 0.6) * g
x = GADKA + 0.35; k = 0
while x < DROP - 0.02:
    add(mixB, snare(0.25 + 0.5 * (x - GADKA) / (DROP - GADKA)), x); k += 1
    x += max(0.05, 0.14 - 0.012 * k)
# drop + beat
def kick(g=1.0):
    t = tt(0.4); f = 48 + 120 * np.exp(-t / 0.03)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.4, 0.001, 0.16) * 2) * g
def hat(d=0.05, g=1.0):
    t = tt(d); return hp(rng.normal(0, 1, len(t)), 3) * env(d, 0.0005, d / 3) * g
def clap(g=1.0):
    out = np.zeros(int(0.25 * SR))
    for o in (0, 0.012, 0.024):
        s = hp(rng.normal(0, 1, int(0.2 * SR)), 4) * env(0.2, 0.001, 0.045 if o < .02 else 0.09); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.5 * g
def b808(f, d=0.42):
    t = tt(d); ff = f * (1 + 0.6 * np.exp(-t / 0.02))
    return np.tanh(np.sin(2 * np.pi * np.cumsum(ff) / SR) * env(d, 0.002, 0.3) * 2.2) * 0.55
t = tt(1.4); boom = np.sin(2 * np.pi * np.cumsum(40 + 100 * np.exp(-t / 0.08)) / SR) * env(1.4, 0.001, 0.6)
crash = hp(rng.normal(0, 1, len(t)), 3) * env(1.4, 0.001, 0.45) * 0.35
add(mixB, boom * 0.9 + crash, DROP)
roots = [55.0, 55.0, 65.41, 49.0]
b = 0; x = DROP
while x < TOTAL - 0.3:
    inrec = RECEIPT <= x < END
    g = 0.45 if inrec else 1.0
    add(mixB, kick(0.95 * g), x)
    if b % 2 == 1: add(mixB, clap(g * (0.6 if inrec else 1)), x)
    add(mixB, hat(0.04, 0.25 * g), x + BEAT / 2)
    add(mixB, hat(0.03, 0.12 * g), x + BEAT / 4); add(mixB, hat(0.03, 0.12 * g), x + 3 * BEAT / 4)
    if b % 8 == 7:
        for r in range(4): add(mixB, hat(0.025, 0.18 * g), x + r * BEAT / 4 + BEAT / 8)
    if not inrec or b % 2 == 0: add(mixB, b808(roots[(b // 4) % 4]), x, 0.8 * g)
    b += 1; x += BEAT
# whoosh na cięciach montażu
acc = 0
for k in CUTB[:-1]:
    acc += k
    w = hp(rng.normal(0, 1, int(0.12 * SR)), 4) * np.linspace(0, 1, int(0.12 * SR)) ** 2
    add(mixB, w * 0.25, DROP + acc * BEAT - 0.12)
# migawka kamery + kliknięcie AF, zmiany światła
add(mixB, hp(rng.normal(0, 1, int(0.03 * SR)), 2) * env(0.03, 0.0005, 0.008) * 0.6, DROP + 2 * BEAT + 0.45)
for q in range(4):
    t_ = tt(0.06); add(mixB, np.sin(2 * np.pi * (1400 + 300 * q) * t_) * env(0.06, 0.001, 0.02) * 0.18, DROP + 4 * BEAT + q * BEAT / 2)
# drukarka
for x in ROWT:
    for c in range(6):
        add(mixB, hp(rng.normal(0, 1, int(0.008 * SR)), 2) * 0.35, x + c * 0.03)
    t = tt(0.18); add(mixB, np.sin(2 * np.pi * 620 * t) * 0.05, x)
# ka-ching
t = tt(1.0); kc = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / dc) for f, a, dc in [(2093, .35, .5), (3136, .25, .4), (4186, .15, .3), (2637, .2, .45)])
add(mixB, kc, TOT + 0.02); add(mixB, hp(rng.normal(0, 1, int(0.06 * SR)), 2) * env(0.06, 0.001, 0.02) * 0.5, TOT)
# pieczątka
add(mixB, kick(1.2), STAMP); add(mixB, hp(rng.normal(0, 1, int(0.2 * SR)), 6) * env(0.2, 0.001, 0.05) * 0.5, STAMP)
# końcowe uderzenie
add(mixB, boom * 0.6 + crash * 0.8, END)
mix = mixA + mixB
mix = mix[:int(TOTAL * SR)]
fo = int(0.5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
mix = np.tanh(mix * 1.15); mix = mix / np.abs(mix).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (mix * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))

# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", "8766"], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto("http://127.0.0.1:8766/index.html")
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
