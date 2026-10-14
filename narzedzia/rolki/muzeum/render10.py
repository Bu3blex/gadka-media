"""Rolka „Muzeum niedokończonych podcastów”."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_muzeum.mp4")
PORT = 8774
FPS, SR = 30, 44100
EX = [1300, 2500, 3700, 4900, 6000, 7300, 8400, 9500, 10700]
KF = [[0, 0], [3.3, 0], [4.2, 1300], [6.9, 1300], [7.7, 2500], [10.4, 2500], [11.2, 3700], [13.9, 3700], [14.7, 4900], [17.4, 4900],
      [18.1, 6000], [18.6, 6000], [19.6, 7300], [21.0, 7300], [21.6, 8400], [23.0, 8400], [23.6, 9500], [25.0, 9500], [25.7, 10700]]
DOOR, WALK, FIN, TOTAL = 18.15, 18.85, 25.7, 30.5
G = [[1, 'Kupiony w poniedziałek. W pudełku do dziś.', 4.3, 6.9, 1],
     [2, 'Debiut. Słychać lodówkę, sąsiada i echo.', 7.8, 10.4, 1],
     [3, 'Pomysłów: 47. Nagranych: 0.', 11.3, 13.9, 1],
     [4, 'Najdłużej eksponowane dzieło w kolekcji.', 14.8, 17.4, 1],
     [5, 'Prosimy kierować się do wyjścia.', 17.5, 18.7, 1],
     [6, 'Wszystko podłączone. Wystarczy mówić.', 19.7, 22.9, 0],
     [7, 'A pliki zabierasz od razu ze sobą.', 23.1, 25.4, 0]]
DATA = dict(EX=EX, KF=KF, SPLIT=6250, DOOR=DOOR, WALK=WALK, FIN=FIN, TOTAL=TOTAL, G=G)
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(DATA, ensure_ascii=False) + ";")

rng = np.random.default_rng(51)
L = int(TOTAL * SR) + 4 * SR
dry = np.zeros(L); wet = np.zeros(L); late = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0, buf=None):
    b = dry if buf is None else buf
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: b[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def noise(d): return rng.normal(0, 1, int(d * SR))
def piano(f, d=2.5, g=1.0):
    t = tt(d)
    s = sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t / (dc)) for h, a, dc in ((1, 1, 1.2), (2, .4, .6), (3, .2, .3), (4, .1, .2)))
    return s * np.minimum(1, t / 0.004) * g
def pad(fs, d, g=1.0):
    t = tt(d); s = sum(np.sin(2 * np.pi * f * t + 0.4 * np.sin(2 * np.pi * 0.3 * t)) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in fs) / len(fs)
    return s * np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.8) * g
def step(g=1.0):
    d = 0.08; return (hp(noise(d), 3) * env(d, 0.0005, 0.008) * 0.8 + np.sin(2 * np.pi * 180 * tt(d)) * env(d, 0.0005, 0.015) * 0.4) * g
def beep(f=1400, g=1.0): t = tt(0.12); return np.sin(2 * np.pi * f * t) * env(0.12, 0.003, 0.05) * g
def kick(g=1.0):
    t = tt(0.25); return np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-t / 0.02)) / SR) * env(0.25, 0.001, 0.1) * g

# sala 1: ciemne, rzadkie pianino (d-moll), pogłos
hall1 = [(146.83, [293.66, 349.23, 440.0, 523.25]), (116.54, [293.66, 349.23, 466.16, 587.33]), (130.81, [261.63, 329.63, 392.0, 466.16]), (110.0, [277.18, 329.63, 392.0, 440.0])]
x = 0.6; k = 0
while x < WALK - 0.4:
    r, ch = hall1[k % 4]
    add(piano(r, 3, 0.25), x, 1, wet)
    for j, f in enumerate(ch): add(piano(f, 2.5, 0.07), x + 0.35 + j * 0.45, 1, wet)
    add(pad([r * 2, ch[1], ch[2]], 2.6, 0.05), x, 1, wet)
    x += 2.4; k += 1
# szum sali
t = tt(WALK); add(lpf(noise(WALK), 60)[:len(t)] * 0.15, 0)
# klik światła
add(lpf(noise(0.05), 3) * env(0.05, 0.0005, 0.01) * 1.2, 0.22, 1, wet); add(kick(0.5), 0.22, 1, wet)
# kroki przy przejazdach kamery
for i in range(len(KF) - 1):
    t0, x0 = KF[i]; t1, x1 = KF[i + 1]
    if x0 != x1:
        n = int((t1 - t0) / 0.32)
        for s in range(n): add(step(0.5 if t0 < WALK else 0.3), t0 + 0.05 + s * 0.32, 1, wet if t0 < WALK else None)
for n, s, t0, t1, dk in G: add(beep(1500 if dk else 1800, 0.15), t0)
# neon
t = tt(17.6 - 14.3); bz = (np.sin(2 * np.pi * 100 * t) + 0.5 * np.sign(np.sin(2 * np.pi * 200 * t)) * 0.3) * np.minimum(1, t / 0.3) * np.minimum(1, (t[-1] - t) / 0.3)
fl = np.repeat(rng.random(int(len(t) / (SR / 14)) + 2) > 0.12, int(SR / 14))[:len(t)]
add(bz * fl * 0.06, 14.3)
# drzwi
t = tt(0.7); add(lpf(np.sin(2 * np.pi * np.cumsum(300 + 200 * np.sin(2 * np.pi * 3 * t)) / SR), 3) * np.sin(np.pi * t / 0.7) * 0.05, DOOR, 1, wet)
n = int(1.0 * SR); add(np.linspace(0, 1, n) ** 2 * hp(noise(1.0), 4) * 0.2, WALK - 1.0)
# sala 2: jasna, ciepła, rytm
B = 60 / 96; x = WALK; b = 0
hall2 = [(130.81, [523.25, 659.25, 783.99]), (174.61, [523.25, 698.46, 880.0]), (110.0, [523.25, 659.25, 880.0]), (196.0, [587.33, 783.99, 987.77])]
while x < TOTAL - 0.4:
    r, ch = hall2[(b // 4) % 4]
    if b % 4 == 0:
        add(pad([r * 2] + ch, 4 * B + 0.5, 0.10), x)
        add(piano(r, 2, 0.3), x)
    add(piano(ch[b % 3] * (2 if b % 2 else 1), 1.2, 0.09), x + B / 2)
    add(kick(0.45), x) if b % 2 == 0 else add(hp(noise(0.12), 3) * env(0.12, 0.001, 0.04) * 0.15, x)
    add(hp(noise(0.03), 2) * env(0.03, 0.0005, 0.008) * 0.08, x + B / 2)
    x += B; b += 1
for j, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(piano(f, 2.5, 0.2), WALK + j * 0.05)
for j, f in enumerate([1046.5, 1318.5, 1568.0]): add(piano(f, 2, 0.12), FIN + 0.5 + j * 0.12)

# pogłos sali muzealnej
n = int(2.8 * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / 0.55); ir = lpf(ir, 5); ir /= np.sqrt((ir ** 2).sum()) * 2.2
rv = np.convolve(wet, ir)[:L]
m = dry + wet * 0.6 + rv
m = m[:int(TOTAL * SR)]
fo = int(0.8 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.1); m = m / np.abs(m).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2))
# ---------------- obraz
srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=WD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
prev = os.environ.get("PREV")
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_function("window.READY===true", timeout=20000)
        def shot(t):
            pg.evaluate(f"renderAt({t})")
            return pg.screenshot(type="jpeg", quality=93)
        if prev:
            ims = []
            for t in [float(x) for x in prev.split(",")]:
                open(WD + "/_f.jpg", "wb").write(shot(t)); ims.append(Image.open(WD + "/_f.jpg").resize((270, 480)))
            sh = Image.new("RGB", (280 * len(ims), 480), "white")
            for i, im in enumerate(ims): sh.paste(im, (i * 280, 0))
            sh.save(WD + "/prev.jpg"); sys.exit()
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg", "-r", str(FPS), "-i", "-", "-i", wav,
                               "-shortest", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS); t0 = time.time()
        for i in range(n):
            ff.stdin.write(shot(i / FPS))
            if i % 150 == 0: print(i, n, round(time.time() - t0, 1), flush=True)
        ff.stdin.close(); ff.wait()
        print("ok", OUT)
finally:
    srv.terminate()
