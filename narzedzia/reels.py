import sys, os, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from design import *

W, H, FPS = 1080, 1920, 30
M = 80
OUT = os.path.join(os.environ.get("GADKA_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")), "rolki")
os.makedirs(OUT, exist_ok=True)


def overlay(kicker, head, head2=None, sub=None, cta=None):
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    maxw = W - 2 * M - 60
    fh = font("black", 112)
    lh = round(112 * 1.03)
    n = len(wrap(d, head, fh, maxw)) + (len(wrap(d, head2, fh, maxw)) if head2 else 0)
    fs = font("med", 46)
    ns = len(wrap(d, sub, fs, maxw)) if sub else 0
    y = 1430 - lh * n - (ns * 60 + 20 if sub else 0) - (110 if cta else 0)
    if kicker:
        pill(d, M, y - 104, kicker, font("bold", 34))
    y = text_block(d, M, y, head, fh, WHITE, maxw, lh=1.03)
    if head2:
        y = text_block(d, M, y, head2, fh, ORANGE, maxw, lh=1.03)
    if sub:
        y = text_block(d, M, y + 20, sub, fs, CREAM, maxw, lh=1.3)
    if cta:
        pill(d, M, y + 44, cta, font("bold", 42), bg=WHITE, fg=NAVY)
    return o


def base(code):
    im = cover(code, round(W * 1.12), round(H * 1.12))
    shade = Image.new("L", (1, im.height), 0)
    for y in range(im.height):
        t = max(0, (y - im.height * 0.28) / (im.height * 0.42))
        shade.putpixel((0, y), round(min(1, t) ** 1.25 * 238))
    return Image.composite(Image.new("RGB", im.size, NAVY), im, shade.resize(im.size))


def render(name, scenes):
    path = os.path.join(OUT, name + ".mp4")
    total = sum(s[1] for s in scenes)
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wordmark(ImageDraw.Draw(wm), M + 22, 210, 38)
    prev_last = None
    for idx, (code, dur, ov) in enumerate(scenes):
        b = base(code)
        n = round(dur * FPS)
        zin = idx % 2 == 0
        for f in range(n):
            t = f / max(1, n - 1)
            z = 1.0 + 0.10 * (t if zin else 1 - t)  # crop scale factor relative to frame
            cw, ch = b.width / z, b.height / z
            x0 = (b.width - cw) / 2
            y0 = (b.height - ch) / 2
            fr = b.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
            # text: fade + slide in during first 0.35 s
            a = min(1, f / (0.35 * FPS))
            ease = 1 - (1 - a) ** 3
            if ease > 0:
                o = ov.copy()
                if ease < 1:
                    alpha = o.getchannel("A").point(lambda v: round(v * ease))
                    o.putalpha(alpha)
                fr.alpha_composite(o, (0, round(40 * (1 - ease))))
            fr.alpha_composite(wm)
            fr = fr.convert("RGB")
            # short crossfade from the previous scene
            if prev_last is not None and f < 5:
                fr = Image.blend(prev_last, fr, (f + 1) / 6)
            p.stdin.write(fr.tobytes())
            last = fr
        prev_last = last
    p.stdin.close()
    p.wait()
    return path, total


R = {
    "2026-10-08_rolka_4-klimaty": [
        ("037", 2.3, overlay("ROLKI I PODCASTY", "1 studio,", "4 klimaty")),
        ("044", 1.6, overlay("01", "Lamele")),
        ("010", 1.6, overlay("02", "Granatowa zasłona")),
        ("019", 1.6, overlay("03", "Biała cegła")),
        ("028", 1.6, overlay("04", "Okrągły stół")),
        ("041", 2.8, overlay(None, "Wszystkie", "w jednej sesji", "2 godziny od 300 zł netto", "Link w bio  →")),
    ],
    "2026-10-13_rolka_300-zl": [
        ("056", 2.4, overlay("GADKA STUDIO", "Co dostajesz", "za 300 zł?")),
        ("041", 1.5, overlay(None, "2 godziny", "w studiu")),
        ("037", 1.5, overlay(None, "2 kamery 4K")),
        ("059", 1.5, overlay(None, "4× Shure SM7B")),
        ("050", 1.5, overlay(None, "Mikser", "RØDECaster Pro")),
        ("013", 1.5, overlay(None, "15+ aranżacji")),
        ("053", 1.5, overlay(None, "Pliki", "od ręki")),
        ("022", 2.8, overlay(None, "Wszystko", "za 300 zł netto", "Bez dopłat za sprzęt i scenografię.", "Link w bio  →")),
    ],
    "2026-10-20_rolka_pierwszy-raz": [
        ("034", 2.6, overlay("POV", "Pierwszy raz", "w studiu podcastowym")),
        ("031", 2.0, overlay(None, "Tyle sprzętu…", "od czego zacząć?")),
        ("016", 2.0, overlay(None, "15 minut", "szkolenia", "Pokazujemy kamery, światło i mikrofony.")),
        ("047", 1.8, overlay(None, "Ustawiasz kadr", "po swojemu")),
        ("001", 1.8, overlay(None, "I nagrywasz", "bez stresu")),
        ("041", 2.8, overlay(None, "Twój pierwszy", "odcinek?", "Szkolenie nie wlicza się w czas wynajmu.", "Link w bio  →")),
    ],
    "2026-10-27_rolka_gdzie-haczyk": [
        ("028", 2.6, overlay(None, "300 zł za 2 h", "w studiu z 4K?")),
        ("044", 1.6, overlay(None, "Gdzie", "haczyk?")),
        ("059", 1.6, overlay(None, "Mikrofony w cenie?", "Tak.")),
        ("010", 1.6, overlay(None, "Światło i tła?", "Tak.")),
        ("053", 1.6, overlay(None, "Pliki od ręki?", "Tak.")),
        ("019", 2.2, overlay("HACZYK", "Montujesz", "sam.")),
        ("041", 2.8, overlay(None, "Tyle.", "Reszta jest w cenie.", "2 godziny od 300 zł netto.", "Link w bio  →")),
    ],
}

if __name__ == "__main__":
    only = sys.argv[1:] or list(R)
    for k in only:
        print(render(k, R[k]))
