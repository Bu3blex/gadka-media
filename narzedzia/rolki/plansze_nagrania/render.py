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

# ---------------- OŚ CZASU (nu-disco 116 BPM): plansza ↔ nagranie, po takcie
BPM = 116; B = 60 / BPM; BAR = 4 * B
SEG = [["P", "Jeden podcast.", "Wiele scenografii."], ["V", "a1", "BIAŁA KOSTKA"],
       ["P", "Ta sama rozmowa.", "Inna scenografia."], ["V", "b1", "CIEMNA ZASŁONA"],
       ["SPEC"], ["V", "e1", "DWIE KAMERY 4K"],
       ["PRICE"], ["V", "b4", "STÓŁ RADIOWY"], ["FIN"]]
SEG = [[i * BAR] + s for i, s in enumerate(SEG)]
FINT = SEG[-1][0]
TOTAL = FINT + 1.7 * BAR
E = dict(B=SEG[1][0], C=SEG[3][0], D=SEG[4][0], E=FINT)
DATA = dict(SC=[0.0], TOTAL=TOTAL, PHOTOS=[], E=E, B=B, SEG=SEG)
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

# ---------------- MUZYKA: nu-disco (Dm9 – G13 – Cmaj9 – Am7), basowe oktawy, otwarte hi-haty na offbeat
def ohat(g=1.0): return hp(noise(0.16), 2) * env(0.16, 0.002, 0.06) * g
def stab(fs, d=0.18, g=1.0): t = tt(d); s = sum(saw(f, t) + saw(f * 1.004, t) for f in fs) / (2 * len(fs)); return lpf(s, 5) * env(d, 0.003, 0.07) * g
CH = [[293.66, 349.23, 440.0, 523.25, 659.25], [196.0, 246.94, 349.23, 440.0, 659.25], [261.63, 329.63, 392.0, 493.88, 587.33], [220.0, 261.63, 329.63, 392.0]]
RT = [73.42, 49.0, 65.41, 55.0]
nb = int(TOTAL / B) + 1
for b in range(nb):
    x = b * B; bar = (b // 4) % 4; c = CH[bar]
    if x >= TOTAL - 0.6: break
    soft = x < 0.5 * BAR
    add(kick(0.0 if soft else 0.75), x, 1, mus)
    if b % 2: add(clap(0.5), x, 1, mus)
    add(ohat(0.12), x + B / 2, 1, mus); add(hat(0.02, 0.06), x + B / 4, 1, mus); add(hat(0.02, 0.06), x + 3 * B / 4, 1, mus)
    for k, o in enumerate([0, 0.5, 0.75]): add(bass(RT[bar] * (2 if k == 1 else 1), B * 0.3, 0.3), x + o * B, 1, mus)
    if b % 2 == 0: add(stab(c[1:4], 0.2, 0.09), x + B * 0.5, 1, wet)
    if b % 4 == 3: add(stab(c[2:5], 0.16, 0.07), x + B * 0.75, 1, wet)
    if b % 4 == 0: add(pad(c[:3], 4 * B, 0.03, 12), x, 1, mus)
# ---------------- EFEKTY (oszczędnie)
for s in SEG[1:]: add(lpf(whoosh(0.35, 0.16), 3), s[0] - 0.3)
for k, f in enumerate([587.33, 739.99, 880.0, 1174.66]): add(bell(f, 1.8, 0.07), FINT + 0.4 + k * 0.07, 1, wet)

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
            pg.evaluate("renderCover()"); pg.screenshot(path=os.path.join(WD, "okladka.jpg"), type="jpeg", quality=95); print("okladka.jpg"); sys.exit()
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
