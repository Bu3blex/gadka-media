"""Rolka „Tarot dla podcasterów”."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_tarot.mp4")
PORT = 8776
FPS, SR = 30, 44100
R = [[2.6, 3.3, 6.8], [7.1, 7.8, 11.3], [11.6, 12.6, 16.0]]
KN = 14.8; END = 16.4; TOTAL = 22.0
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(dict(R=R, KN=KN, END=END, TOTAL=TOTAL)) + ";")

rng = np.random.default_rng(71)
L = int(TOTAL * SR) + 3 * SR
dry = np.zeros(L); wet = np.zeros(L)
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
def harp(f, d=1.6, g=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.3) + 0.1 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.1)) * env(d, 0.002, 0.6) * g
def bell(f, d=2.0, g=1.0):
    t = tt(d); parts = ((1, .5, .9), (2.76, .25, .4), (5.4, .12, .2), (8.9, .05, .1))
    return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t / dc) for p, a, dc in parts) * np.minimum(1, t / .002) * g
def drone(fs, d, g=1.0):
    t = tt(d); s = sum(np.sin(2 * np.pi * f * t + 0.5 * np.sin(2 * np.pi * 0.13 * t)) for f in fs) / len(fs)
    return s * np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.0) * g
def whoosh(d=0.5, g=1.0):
    n = int(d * SR); return lpf(hp(noise(d), 4), 3) * np.sin(np.linspace(0, np.pi, n)) ** 2 * g
def kick(g=1.0):
    t = tt(0.3); return np.sin(2 * np.pi * np.cumsum(48 + 90 * np.exp(-t / 0.02)) / SR) * env(0.3, 0.001, 0.12) * g
def shaker(g=1.0): n = int(0.06 * SR); return hp(noise(0.06), 2) * np.sin(np.linspace(0, np.pi, n)) * g

# D-moll: dron + arpeggia harfy
add(drone([73.42, 110.0, 146.83], R[2][1], 0.22), 0.0)
arp = [293.66, 349.23, 440.0, 587.33, 523.25, 440.0, 349.23, 329.63]
x = 0.2; k = 0
while x < R[2][1] - 0.3:
    add(harp(arp[k % 8], 1.6, 0.11), x, 1, wet); x += 0.33; k += 1
# rozdanie kart
for i in range(3): add(whoosh(0.35, 0.3), 0.2 + i * 0.18)
for i, (s, f, b) in enumerate(R):
    add(whoosh(0.6, 0.45), s - 0.05)
    add(hp(noise(0.05), 2) * env(0.05, 0.0005, 0.01) * 0.5, f + 0.25)  # klap karty
    for j, fr in enumerate([1174.66, 1396.91, 1760.0] if i < 2 else []): add(bell(fr, 1.8, 0.10), f + 0.25 + j * 0.06, 1, wet)
    add(whoosh(0.5, 0.3), b - 0.05)
for j, fr in enumerate([1760.0, 2093.0, 2637.0, 3136.0]): add(bell(fr, 1.5, 0.07), R[2][2] + j * 0.05, 1, wet)
for j, fr in enumerate([587.33, 739.99, 880.0]): add(bell(fr, 2, 0.08), KN + j * 0.1, 1, wet)
# karta 2: echo – powtórzone dzwonki
for j in range(5): add(bell(880, 0.6, 0.12 * 0.6 ** j), R[1][1] + 0.9 + j * 0.25, 1, wet)
# karta 3: magiczne narastanie i rozwiązanie w D-dur
s3, f3 = R[2][0], R[2][1]; d = f3 + 0.25 - s3; t = tt(d)
add(hp(noise(d), 3)[:len(t)] * (t / d) ** 2 * 0.25, s3, 1, wet)
add(np.sin(2 * np.pi * np.cumsum(300 + 900 * (t / d) ** 2) / SR) * (t / d) ** 2 * 0.08, s3, 1, wet)
for j, fr in enumerate([587.33, 739.99, 880.0, 1174.66, 1479.98, 1760.0]): add(bell(fr, 2.5, 0.13), f3 + 0.25 + j * 0.05, 1, wet)
add(kick(0.7), f3 + 0.25)
# ciepły groove od karty 3 do końca (D-dur, 92 BPM)
B = 60 / 92; x = f3 + 0.25; k = 0
ch = [[146.83, 220.0, 293.66, 369.99], [123.47, 185.0, 246.94, 293.66], [98.0, 196.0, 246.94, 293.66], [110.0, 220.0, 277.18, 329.63]]
add(drone([73.42, 110.0, 146.83, 185.0], TOTAL - x, 0.18), x)
while x < TOTAL - 0.5:
    c = ch[(k // 4) % 4]
    if k % 2 == 0: add(kick(0.55), x)
    add(shaker(0.08), x + B / 2)
    add(harp(c[k % 4] * 2, 1.2, 0.10), x, 1, wet); add(harp(c[(k + 2) % 4] * 2, 1.0, 0.07), x + B / 2, 1, wet)
    x += B; k += 1
for j, fr in enumerate([587.33, 739.99, 880.0]): add(bell(fr, 2, 0.1), END + 0.5 + j * 0.08, 1, wet)

n = int(2.5 * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / 0.6); ir = lpf(ir, 4); ir /= np.sqrt((ir ** 2).sum()) * 2.0
m = dry + wet * 0.7 + np.convolve(wet, ir)[:L]
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
            pg.evaluate(("window.SAFE=1;" if os.environ.get("SAFE") else "") + f"renderAt({t})")
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
