"""Rolka „Twoje podsumowanie roku jako podcaster”."""
import os, sys, json, time, wave, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

WD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WD, "..", "ai", "rolka_podsumowanie.mp4")
PORT = 8775
FPS, SR = 30, 44100
B = 60 / 124
beats = [0, 5, 11, 18, 23, 29, 35, 40, 48]   # starty scen w uderzeniach
SC = [b * B for b in beats]
TOTAL = (48 + 9) * B
open(os.path.join(WD, "data.js"), "w").write("window.DATA=" + json.dumps(dict(SC=SC, TOTAL=TOTAL)) + ";")

rng = np.random.default_rng(61)
L = int(TOTAL * SR) + 3 * SR
mix = np.zeros(L); mus = np.zeros(L)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0, buf=None):
    b = mix if buf is None else buf
    i = int(at * SR); j = min(L, i + len(sig))
    if 0 <= i < L: b[i:j] += sig[:j - i] * g
def env(d, a=0.003, dec=0.1):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / dec)
def hp(x, k=8): return x - np.convolve(x, np.ones(k) / k, "same")
def lpf(x, k=20): return np.convolve(x, np.ones(k) / k, "same")
def noise(d): return rng.normal(0, 1, int(d * SR))
def saw(f, t): return 2 * ((f * t) % 1) - 1
def kick(g=1.0):
    t = tt(0.3); return np.tanh(np.sin(2 * np.pi * np.cumsum(46 + 130 * np.exp(-t / 0.025)) / SR) * env(0.3, 0.001, 0.13) * 2.5) * g
def clap(g=1.0):
    out = np.zeros(int(0.25 * SR))
    for o in (0, 0.009, 0.018):
        s = hp(noise(0.2), 4) * env(0.2, 0.001, 0.045); i = int(o * SR); out[i:i + len(s)] += s
    return out * 0.45 * g
def hat(d=0.04, g=1.0): return hp(noise(d), 2) * env(d, 0.0005, d / 3) * g
def supersaw(fs, d, g=1.0, cut=6):
    t = tt(d); s = sum(saw(f * dt, t) for f in fs for dt in (0.993, 1.0, 1.007)) / (3 * len(fs))
    return lpf(s, cut) * g
def pluck(f, d=0.25, g=1.0):
    t = tt(d); return lpf(saw(f, t) + saw(f * 1.005, t), 4) * env(d, 0.002, 0.08) * g
def bass(f, d, g=1.0):
    t = tt(d); return np.tanh((np.sin(2 * np.pi * f * t) + 0.4 * saw(f, t)) * 1.6) * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.01) * g
def pop(f=900, g=1.0):
    t = tt(0.09); return np.sin(2 * np.pi * np.cumsum(f + 1100 * np.exp(-t / 0.012)) / SR) * env(0.09, 0.001, 0.03) * g
def whoosh(d=0.35, g=1.0):
    n = int(d * SR); return hp(noise(d), 4) * np.linspace(0, 1, n) ** 2 * g

# progresja F – Am – Dm – Bb (pogodny pop)
CH = [[349.23, 440.0, 523.25], [329.63, 440.0, 523.25], [293.66, 349.23, 440.0], [293.66, 349.23, 466.16]]
RT = [87.31, 110.0, 73.42, 58.27]
def groove(b0, b1, full=True, g=1.0):
    for b in range(b0, b1):
        x = b * B; bar = (b // 4) % 4
        add(kick(0.85), x, g, mus)
        if b % 2 == 1: add(clap(0.7), x, g, mus)
        add(hat(0.04, 0.16), x + B / 2, g, mus)
        if full: add(hat(0.025, 0.08), x + B / 4, g, mus); add(hat(0.025, 0.08), x + 3 * B / 4, g, mus)
        # bas offbeat
        add(bass(RT[bar], B / 2 - 0.02, 0.35), x + B / 2, g, mus)
        # akord – pluck na ósemkach
        c = CH[bar]
        for k in range(2):
            add(pluck(c[(b * 2 + k) % 3] * 2, 0.22, 0.10), x + k * B / 2, g, mus)
        if b % 4 == 0: add(supersaw(c, 4 * B, 0.05 if full else 0.03, 8) * np.minimum(1, tt(4 * B) / 0.05), x, g, mus)
groove(0, 35, full=True)
# zwrot akcji: przerwa (35–40), tylko pad + riser
x0 = 35 * B; d = 5 * B
add(supersaw([174.61, 220.0, 261.63], d, 0.05, 20) * np.minimum(1, tt(d) / 0.2), x0, 1, mus)
t = tt(d); add(hp(noise(d), 3)[:len(t)] * (t / d) ** 2.5 * 0.3, x0, 1, mus)
add(np.sin(2 * np.pi * np.cumsum(200 + 1200 * (t / d) ** 2) / SR) * (t / d) ** 2 * 0.1, x0, 1, mus)
groove(40, 57, full=True, g=1.1)
# efekty
for s in SC[1:]: add(whoosh(0.3, 0.4), s - 0.28); add(pop(800, 0.35), s)
# hak
for k in range(3): add(pop(700 + 200 * k, 0.4), SC[0] + k * 0.12)
# licznik: tykanie i „bęc” na zero
for k in range(int(1.25 * 22)): add(hp(noise(0.012), 2) * 0.15, SC[1] + 0.35 + k / 22)
t = tt(0.6); add(np.sin(2 * np.pi * np.cumsum(220 * np.exp(-t / 0.4) + 60) / SR) * env(0.6, 0.002, 0.25) * 0.45, SC[1] + 1.25)  # zjazd w dół
add(pop(600, 0.5), SC[1] + 1.5)
for k in range(3): add(pop(900 + 150 * k, 0.4), SC[2] + 0.6 + k * 0.5)
add(pop(1300, 0.5), SC[3] + 0.55)
for k in range(3): add(whoosh(0.25, 0.25), SC[4] + 0.5 + k * 0.35)
add(pop(1000, 0.5), SC[5] + 0.45)
# zwrot: „przewijanie taśmy”
t = tt(0.5); add(lpf(saw(1, t) * 0 + np.sin(2 * np.pi * np.cumsum(1400 - 1200 * t / 0.5) / SR), 3) * env(0.5, 0.005, 0.3) * 0.3, SC[6])
for k in range(4): add(pop(700 + 120 * k, 0.45), SC[7] + 1.0 + k * 0.35)
for k in range(3): add(pop(800 + 200 * k, 0.4), SC[7] + k * 0.35)
add(pop(1500, 0.5), SC[8] + 0.7)
mix[:] += mus * 0.7
m = mix[:int(TOTAL * SR)]
fo = int(0.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)
m = np.tanh(m * 1.15); m = m / np.abs(m).max() * 0.93
wav = os.path.join(WD, "_mix.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    a = (m * 32767).astype(np.int16); w.writeframes(np.repeat(a[:, None], 2, 1).tobytes())
print("audio ok", round(TOTAL, 2), [round(s, 2) for s in SC])
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
