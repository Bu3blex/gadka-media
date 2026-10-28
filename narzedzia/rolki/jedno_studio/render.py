"""SZABLON renderu rolki: oś czasu -> data.js, dźwięk (numpy) -> _mix.wav, klatki (Playwright) -> MP4.

Użycie (w folderze rolki):
  PREV=1.0,4.5,9.0 python3 render.py        # podgląd wybranych klatek -> prev.jpg
  SAFE=1 PREV=... python3 render.py         # podgląd z ramką strefy bezpiecznej
  COVER=1 python3 render.py                 # okładka -> okladka.jpg (renderCover)
  python3 render.py                         # pełny render -> rolka.mp4 + rolka_ig.mp4 (<30 MB)
"""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "rolka.mp4")
PORT = int(os.environ.get("PORT", "8799"))
FPS, SR = 30, 44100

# ---------------- OŚ CZASU (100 BPM, cięcie co takt = 2,4 s)
BPM = 100; B = 60 / BPM; BAR = 4 * B
names = ["hook", "a1", "a2", "a3", "a4", "e1", "e2"]
SHOTS = [[i * BAR, n] for i, n in enumerate(names)]
FIN = len(names) * BAR
TOTAL = FIN + 2 * BAR
DATA = dict(SC=[0.0], TOTAL=TOTAL, PHOTOS=[], SHOTS=SHOTS, FIN=FIN, BAR=BAR, B=B)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA, ensure_ascii=False) + ";")

# ---------------- BIBLIOTEKA DŹWIĘKÓW
rng = np.random.default_rng(1)
L = int(TOTAL * SR) + 3 * SR
mix = np.zeros(L); mus = np.zeros(L); wet = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0, buf=None):
    b = mix if buf is None else buf
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: b[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1): t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def noise(d): return rng.normal(0, 1, int(d * SR))
def saw(f, t): return 2 * ((f * t) % 1) - 1
def kick(g=1.0): t = tt(0.3); return np.tanh(np.sin(2 * np.pi * np.cumsum(46 + 130 * np.exp(-t / 0.025)) / SR) * env(0.3, 0.001, 0.13) * 2.5) * g
def clap(g=1.0):
    out = np.zeros(int(0.25 * SR))
    for o in (0, 0.009, 0.018): s = hp(noise(0.2), 4) * env(0.2, 0.001, 0.045); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.45 * g
def hat(d=0.04, g=1.0): return hp(noise(d), 2) * env(d, 0.0005, d / 3) * g
def bass(f, d, g=1.0): t = tt(d); return np.tanh((np.sin(2 * np.pi * f * t) + 0.4 * saw(f, t)) * 1.6) * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.01) * g
def pluck(f, d=0.25, g=1.0): t = tt(d); return lpf(saw(f, t) + saw(f * 1.005, t), 4) * env(d, 0.002, 0.08) * g
def pad(fs, d, g=1.0, cut=8): t = tt(d); s = sum(saw(f * k, t) for f in fs for k in (0.993, 1, 1.007)) / (3 * len(fs)); return lpf(s, cut) * np.minimum(1, t / 0.05) * g
def rhodes(f, d=1.2, g=1.0):
    t = tt(d); s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.4) + 0.18 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / 0.08)
    return s * np.minimum(1, t / 0.004) * np.exp(-t / 0.9) * g
def bell(f, d=1.2, g=1.0):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in ((1, .5, .6), (2.76, .25, .3), (5.4, .1, .15))) * np.minimum(1, t / .002) * g
def pop(f=900, g=1.0): t = tt(0.09); return np.sin(2 * np.pi * np.cumsum(f + 1100 * np.exp(-t / 0.012)) / SR) * env(0.09, 0.001, 0.03) * g
def whoosh(d=0.35, g=1.0): n = int(d * SR); return hp(noise(d), 4) * np.linspace(0, 1, n) ** 2 * g
def riser(d, g=1.0): t = tt(d); return (hp(noise(d), 3)[:len(t)] * (t / d) ** 2.5 * 0.3 + np.sin(2 * np.pi * np.cumsum(200 + 1200 * (t / d) ** 2) / SR) * (t / d) ** 2 * 0.1) * g
def braam(f=55, d=3.0, g=1.0):
    t = tt(d); s = np.tanh(sum(saw(f * m, t) * a for m, a in ((1, 1), (1.006, .8), (0.994, .8), (2.003, .5), (0.5, .7))) * 0.9)
    return (lpf(lpf(s, 30), 30) * np.minimum(1, t / 0.05) * np.exp(-t / (d * 0.38)) * 0.55 + np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 1.4) * 0.5) * g
def wav_in(path):  # dźwięk z własnego nagrania (klip.sh) -> numpy
    with wave.open(path) as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    return a

# ---------------- MUZYKA: elegancki deep house (Am9 – Fmaj7 – Cmaj7 – Gadd9), ciepły Rhodes, sub bas
def rim(g=1.0): t = tt(0.05); return (np.sin(2 * np.pi * 1600 * t) * 0.5 + hp(noise(0.05), 2) * 0.4) * env(0.05, 0.0005, 0.007) * g
def shk(g=1.0): n = int(0.06 * SR); return hp(noise(0.06), 2) * np.sin(np.linspace(0, np.pi, n)) ** 2 * g
def sub(f, d, g=1.0): t = tt(d); return np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05) * g
CH = [[220.0, 261.63, 329.63, 392.0, 493.88], [174.61, 220.0, 261.63, 329.63], [130.81, 196.0, 246.94, 329.63], [196.0, 246.94, 293.66, 440.0]]
RT = [55.0, 43.65, 65.41, 49.0]
nb = int(TOTAL / B)
for b in range(nb):
    x = b * B; bar = (b // 4) % 4; c = CH[bar]
    intro = x < 0.5 * BAR
    if not intro: add(kick(0.6), x, 1, mus)
    if b % 2 == 1: add(rim(0.14), x, 1, mus)
    add(shk(0.06), x + B / 2, 1, mus); add(shk(0.035), x + B / 4, 1, mus); add(shk(0.035), x + 3 * B / 4, 1, mus)
    if not intro and b % 4 in (0, 2): add(sub(RT[bar], B * 1.6, 0.32), x + (B / 2 if b % 4 == 2 else 0), 1, mus)
    if b % 4 == 0:
        for k, f in enumerate(c): add(rhodes(f, 2.2, 0.055), x + k * 0.01, 1, wet)
        add(pad(c[:3], 4 * B + 0.3, 0.035, 14), x, 1, mus)
    if b % 4 == 2:
        for k, f in enumerate(c[1:4]): add(rhodes(f * 2, 0.8, 0.03), x + B / 2 + k * 0.01, 1, wet)
# ---------------- EFEKTY (subtelne)
for t0, n in SHOTS[1:]: add(lpf(whoosh(0.5, 0.18), 3), t0 - 0.35)
for k in range(3): add(rim(0.3), k * 0.1)
add(kick(1.0), 0.42); add(braam(55, 1.4, 0.45), 0.42); add(pop(900, 0.3), 0.97)
add(kick(0.8), 0.0); add(pop(700, 0.25), 0.35); add(kick(0.7), 0.35)
for k, f in enumerate([880.0, 1108.73]): add(bell(f, 1.2, 0.08), 0.4 + k * 0.06, 1, wet)
add(lpf(whoosh(0.6, 0.22), 3), FIN - 0.4)
for k, f in enumerate([440.0, 523.25, 659.25, 880.0]): add(bell(f, 2.0, 0.07), FIN + 0.9 + k * 0.08, 1, wet)

mix[:] += mus * 0.7
n = int(2.0 * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / 0.5); ir = lpf(ir, 4); ir /= np.sqrt((ir ** 2).sum()) * 2
mix[:] += wet * 0.6 + np.convolve(wet, ir)[:L]
m = mix[:int(TOTAL * SR)]
fo = int(0.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.15); m = m / max(1e-9, np.abs(m).max()) * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(np.repeat((m * 32767).astype(np.int16)[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))

# ---------------- OBRAZ
srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_function("window.READY===true", timeout=30000)
        if os.environ.get("SAFE"): pg.evaluate("window.SAFE_BOX=true")
        def shot(t):
            pg.evaluate(f"renderAt({t})")          # renderAt może być async (klatki nagrań)
            return pg.screenshot(type="jpeg", quality=93)
        if os.environ.get("COVER"):
            pg.evaluate("renderCover()"); time.sleep(0.5); pg.screenshot(path=os.path.join(WD, "okladka.jpg"), type="jpeg", quality=95); print("okladka.jpg"); sys.exit()
        prev = os.environ.get("PREV")
        if prev:
            ims = []
            for t in [float(x) for x in prev.split(",")]:
                open(WD + "/_f.jpg", "wb").write(shot(t)); ims.append(Image.open(WD + "/_f.jpg").resize((270, 480)))
            sh = Image.new("RGB", (280 * len(ims), 480), "white")
            for i, im in enumerate(ims): sh.paste(im, (i * 280, 0))
            sh.save(WD + "/prev.jpg"); print("prev.jpg"); sys.exit()
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-shortest", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS); t0 = time.time()
        for i in range(n):
            ff.stdin.write(shot(i / FPS))
            if i % 150 == 0: print(i, n, round(time.time() - t0, 1), flush=True)
        ff.stdin.close(); ff.wait()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", OUT, "-c:v", "libx264", "-b:v", "7M", "-maxrate", "9M", "-bufsize", "14M",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", OUT.replace(".mp4", "_ig.mp4")])
        print("ok", OUT.replace(".mp4", "_ig.mp4"))
finally:
    srv.terminate()
