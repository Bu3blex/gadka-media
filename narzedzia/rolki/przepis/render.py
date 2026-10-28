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

# ---------------- OŚ CZASU
BPM = 118; B = 60 / BPM
E = dict(ING=2.8, STEP_ING=1.15, STEPS=10.0, SERVE=16.4, FIN=19.6)
SC = [0.0]
TOTAL = 24.0
DATA = dict(SC=SC, TOTAL=TOTAL, PHOTOS=["101", "104", "034"], E=E)
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

# ---------------- MUZYKA: bossa nova (Dmaj7–Em7–F#m7–G6/A7)
def nylon(f, d=0.6, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.15) + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.06)) * env(d, 0.002, 0.25) * g
def rim(g=1.0): t = tt(0.05); return (np.sin(2 * np.pi * 1700 * t) * 0.5 + hp(noise(0.05), 2) * 0.5) * env(0.05, 0.0005, 0.008) * g
def shk(g=1.0): n = int(0.07 * SR); return hp(noise(0.07), 2) * np.sin(np.linspace(0, np.pi, n)) ** 2 * g
CH = [[146.83, 185.0, 220.0, 277.18], [164.81, 196.0, 246.94, 293.66], [185.0, 220.0, 277.18, 329.63], [196.0, 246.94, 293.66, 329.63]]
RT = [73.42, 82.41, 92.5, 98.0]
pat = [0, 1.5, 2.5, 3.5]  # synkopowany rytm akordów (w ćwierćnutach)
bars = int(TOTAL / (4 * B))
for bar in range(bars):
    x0 = bar * 4 * B; c = CH[bar % 4]; r_ = RT[bar % 4]
    end = x0 >= E["FIN"] - 0.1
    for o in pat:
        for k, f in enumerate(c): add(nylon(f * 2, 0.5, 0.06), x0 + o * B + k * 0.012, 1, mus)
    add(nylon(r_, 0.8, 0.35), x0); add(nylon(r_ * 1.5, 0.6, 0.25), x0 + 2 * B)  # bas: pryma i kwinta
    add(nylon(r_, 0.4, 0.2), x0 + 3.5 * B)
    for s in range(8): add(shk(0.07 if s % 2 else 0.11), x0 + s * B / 2, 1, mus)
    for o in (1, 2.5, 3.5) if bar % 2 else (1.5, 3): add(rim(0.18), x0 + o * B, 1, mus)
    add(kick(0.4), x0); add(kick(0.3), x0 + 2.5 * B)
    if bar % 2 == 1 and not end:  # melodia flecikowa
        mel = [587.33, 659.25, 739.99, 880.0, 739.99, 659.25]
        for k, f in enumerate(mel): add(rhodes(f, 0.5, 0.05), x0 + k * B * 0.5 + 0.02, 1, wet)
# ---------------- EFEKTY
for k, f in enumerate([1046.5, 1318.5]): add(bell(f, 1.2, 0.18), 0.05 + k * 0.1, 1, wet)   # „ding” minutnika
t_ = tt(0.25); add(lpf(noise(0.25), 3)[:len(t_)] * env(0.25, 0.002, 0.05) * 0.8, 1.3); add(kick(0.7), 1.3)   # stempel
for i in range(6):
    x = E["ING"] + i * E["STEP_ING"]
    add(whoosh(0.35, 0.25), x + 0.1)
    t_ = tt(0.35); add(np.sin(2 * np.pi * np.cumsum(500 * np.exp(-t_ / 0.05) + 120) / SR) * env(0.35, 0.001, 0.08) * 0.45, x + 0.75)  # plusk
    add(lpf(hp(noise(0.3), 3), 2) * env(0.3, 0.003, 0.08) * 0.25, x + 0.75)
t_ = tt(E["STEPS"] - E["ING"]); add(lpf(hp(noise(E["STEPS"] - E["ING"]), 2), 2)[:len(t_)] * 0.025, E["ING"])  # bulgotanie/syk
for i in range(3): add(whoosh(0.35, 0.3), E["STEPS"] + i * 1.9 - 0.1); add(pop(900 + 150 * i, 0.35), E["STEPS"] + i * 1.9 + 0.2)
for k, f in enumerate([783.99, 987.77, 1174.66, 1567.98]): add(bell(f, 1.6, 0.15), E["SERVE"] + 0.1 + k * 0.06, 1, wet)
add(hp(noise(0.03), 2) * env(0.03, 0.0005, 0.004) * 0.5, E["SERVE"] + 0.4); add(hp(noise(0.03), 2) * env(0.03, 0.0005, 0.004) * 0.5, E["SERVE"] + 0.48)  # brzdęk sztućców
add(pop(1000, 0.35), E["SERVE"] + 0.8)
add(whoosh(0.45, 0.45), E["FIN"] - 0.2)
for k, f in enumerate([587.33, 739.99, 880.0, 1174.66]): add(bell(f, 1.8, 0.13), E["FIN"] + 0.7 + k * 0.07, 1, wet)

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
