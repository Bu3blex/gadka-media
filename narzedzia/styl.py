"""Styl Gadka studio (od 13.10.2026): czarne tło, krem, pomarańcz z logo, Poppins, zaokrąglone karty.
Jeden język dla relacji (1080x1920), karuzel (1080x1350) i rolek (MP4 1080x1920)."""
import os, sys, subprocess
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design
from design import cover, gradient
from relacje_wyroznione import (F, paste_logo, wrap, text, pill, BLACK, CARD, CARD2, CREAM, MUTED, ORANGE)

design.FOCAL.update({"101": .27, "102": .55, "103": .45, "104": .5, "105": .5, "106": .45})
SITE = "gadkastudio.pl"


# ---------------- wspólne klocki ----------------
def rounded(im, radius):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=radius, fill=255)
    return m


def photo_card(canvas, code, x, y, w, h, radius=36, zoom=1.0, fx=None):
    ph = cover(code, w, h, zoom=zoom, fx=fx)
    canvas.paste(ph, (x, y), rounded(ph, radius))
    return y + h


def shade_top(im, h=460, a=220):
    g = Image.new("L", (1, h))
    for yy in range(h):
        g.putpixel((0, yy), round(a * (1 - yy / h) ** 1.5))
    im.paste(Image.new("RGB", (im.width, h), BLACK), (0, 0), g.resize((im.width, h)))


def cards(d, x, y, w, items, num=False, title_size=42, body_size=31, gap=20):
    """items: [(tytuł, opis)] -> karty z pomarańczowym akcentem"""
    ft, fb = F("b", title_size), F("r", body_size)
    for i, (t, b) in enumerate(items):
        lines = wrap(d, b, fb, w - 96) if b else []
        h = 34 + round(title_size * 1.25) + len(lines) * round(body_size * 1.38) + 30
        d.rounded_rectangle((x, y, x + w, y + h), radius=30, fill=CARD)
        d.rounded_rectangle((x, y, x + 12, y + h), radius=6, fill=ORANGE)
        tx = x + 44
        if num:
            n = f"0{i+1}"
            d.text((tx, y + 30), n, font=ft, fill=ORANGE)
            tx += d.textlength(n, font=ft) + 22
        d.text((tx, y + 30), t, font=ft, fill=CREAM)
        yy = y + 34 + round(title_size * 1.25)
        for ln in lines:
            d.text((x + 44, yy), ln, font=fb, fill=MUTED); yy += round(body_size * 1.38)
        y += h + gap
    return y


def bullets(d, x, y, w, items, size=40, sub=None):
    for it in items:
        if isinstance(it, tuple):
            t, s = it
        else:
            t, s = it, None
        d.ellipse((x + 2, y + size * 0.42, x + 26, y + size * 0.42 + 24), fill=ORANGE)
        y = text(d, x + 52, y, t, F("b" if s else "m", size), CREAM, w - 52, lh=1.22)
        if s:
            y = text(d, x + 52, y + 2, s, F("r", round(size * 0.78)), MUTED, w - 52, lh=1.3)
        y += 22
    return y


def cta_pill(d, x, y, w, t="Rezerwacja: " + SITE, center=True):
    return pill(d, x, y, t, F("b", 38), bg=CREAM, fg=BLACK, center_w=w if center else None)


def head_block(d, x, y, w, kicker, title, sub=None, center=True, size=84, title2=None):
    if kicker:
        y = pill(d, x, y, kicker, F("b", 30), center_w=w if center else None) + 34
    y = text(d, x, y, title, F("b", size), CREAM, w, lh=1.08, center=center)
    if title2:
        y = text(d, x, y, title2, F("b", size), ORANGE, w, lh=1.08, center=center)
    if sub:
        y = text(d, x, y + 16, sub, F("r", 38), MUTED, w, lh=1.32, center=center)
    return y


def block_height(kicker, title, sub, w, size=84, title2=None):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    h = (98 if kicker else 0) + len(wrap(d, title, F("b", size), w)) * round(size * 1.08)
    if title2:
        h += len(wrap(d, title2, F("b", size), w)) * round(size * 1.08)
    if sub:
        h += 16 + len(wrap(d, sub, F("r", 38), w)) * round(38 * 1.32)
    return h


# ================= RELACJE 1080x1920 =================
SW, SH, SM = 1080, 1920, 84


def story_card(code, kicker, title, sub=None, title2=None, cta=None, fx=None, items=None):
    """logo + zaokrąglone zdjęcie + nagłówek (+ opcjonalne punkty) + CTA"""
    im = Image.new("RGB", (SW, SH), BLACK); d = ImageDraw.Draw(im)
    paste_logo(im, SW / 2, 200, 300)
    ph_h = 700 if not items else 520
    y = photo_card(im, code, SM, 360, SW - 2 * SM, ph_h, fx=fx) + 56
    y = head_block(d, SM, y, SW - 2 * SM, kicker, title, sub, size=78, title2=title2)
    if items:
        y = bullets(d, SM + 20, y + 40, SW - 2 * SM - 40, items, size=38)
    if cta:
        cta_pill(d, SM, y + 56, SW - 2 * SM, cta)
    return im


def story_full(code, kicker, title, sub=None, title2=None, cta=None, fx=None):
    """zdjęcie na cały ekran + przyciemnienie + logo + nagłówek (jak plansze aranżacji)"""
    im = cover(code, SW, SH, fx=fx)
    bh = block_height(kicker, title, sub, SW - 2 * SM, size=86, title2=title2) + (110 if cta else 0)
    y0 = 1640 - bh
    im = gradient(im, y0 - 560, y0 + 40, bottom_alpha=244, color=BLACK)
    shade_top(im)
    d = ImageDraw.Draw(im)
    paste_logo(im, SW / 2, 200, 300)
    y = head_block(d, SM, y0, SW - 2 * SM, kicker, title, sub, size=86, title2=title2)
    if cta:
        cta_pill(d, SM, y + 50, SW - 2 * SM, cta)
    return im


def story_text(kicker, title, sub=None, title2=None, items=None, card_items=None, cta=None):
    """sama typografia na czarnym tle (jak cennik / jak to działa)"""
    im = Image.new("RGB", (SW, SH), BLACK); d = ImageDraw.Draw(im)
    paste_logo(im, SW / 2, 200, 300)
    body_h = 0
    if card_items: body_h = 190 * len(card_items)
    if items: body_h = 120 * len(items)
    bh = block_height(kicker, title, sub, SW - 2 * SM, size=92, title2=title2) + body_h + (130 if cta else 0)
    y = max(440, (SH - bh) // 2 + 60)
    y = head_block(d, SM, y, SW - 2 * SM, kicker, title, sub, size=92, title2=title2)
    if card_items:
        y = cards(d, SM, y + 56, SW - 2 * SM, card_items)
    if items:
        y = bullets(d, SM + 20, y + 56, SW - 2 * SM - 40, items, size=42)
    if cta:
        cta_pill(d, SM, y + 50, SW - 2 * SM, cta)
    return im


# ================= KARUZELE 1080x1350 =================
CW, CH, CM = 1080, 1350, 80


def c_footer(d, i, n):
    f = F("m", 28)
    d.text((CM, CH - 78), SITE, font=f, fill=MUTED)
    t = f"{i}/{n}"
    d.text((CW - CM - d.textlength(t, font=f), CH - 78), t, font=f, fill=MUTED)


def c_cover(code, kicker, title, title2=None, sub=None, fx=None):
    def make(i, n):
        im = cover(code, CW, CH, fx=fx)
        bh = block_height(kicker, title, sub, CW - 2 * CM, size=92, title2=title2)
        y0 = 1190 - bh
        im = gradient(im, y0 - 420, y0 + 30, bottom_alpha=245, color=BLACK)
        shade_top(im, 380, 210)
        d = ImageDraw.Draw(im)
        paste_logo(im, CW / 2, 70, 240)
        head_block(d, CM, y0, CW - 2 * CM, kicker, title, sub, size=92, title2=title2)
        c_footer(d, i, n)
        return im
    return make


def c_photo(code, kicker, title, sub=None, fx=None):
    def make(i, n):
        im = Image.new("RGB", (CW, CH), BLACK); d = ImageDraw.Draw(im)
        paste_logo(im, CW / 2, 64, 200)
        y = photo_card(im, code, CM, 200, CW - 2 * CM, 640, fx=fx) + 48
        head_block(d, CM, y, CW - 2 * CM, kicker, title, sub, size=68, center=False)
        c_footer(d, i, n)
        return im
    return make


def c_cards(kicker, title, items, num=False):
    def make(i, n):
        im = Image.new("RGB", (CW, CH), BLACK); d = ImageDraw.Draw(im)
        paste_logo(im, CW / 2, 64, 200)
        y = head_block(d, CM, 230, CW - 2 * CM, kicker, title, None, size=72)
        cards(d, CM, y + 44, CW - 2 * CM, items, num=num, title_size=42, body_size=32, gap=18)
        c_footer(d, i, n)
        return im
    return make


def c_bullets(kicker, title, items):
    def make(i, n):
        im = Image.new("RGB", (CW, CH), BLACK); d = ImageDraw.Draw(im)
        paste_logo(im, CW / 2, 64, 200)
        y = head_block(d, CM, 240, CW - 2 * CM, kicker, title, None, size=72)
        bullets(d, CM + 20, y + 56, CW - 2 * CM - 40, items, size=42)
        c_footer(d, i, n)
        return im
    return make


def c_prices(kicker="CENNIK", title="Płacisz tylko za czas"):
    rows = [("2 h", "300 zł", "Rolki, shortsy, krótka rozmowa"), ("4 h", "500 zł", "Pełny odcinek podcastu"),
            ("6 h", "750 zł", "Kilka odcinków"), ("8 h", "1000 zł", "Cały dzień w studiu")]

    def make(i, n):
        im = Image.new("RGB", (CW, CH), BLACK); d = ImageDraw.Draw(im)
        paste_logo(im, CW / 2, 64, 200)
        y = head_block(d, CM, 220, CW - 2 * CM, kicker, title, None, size=72) + 44
        for k, (h, p, desc) in enumerate(rows):
            d.rounded_rectangle((CM, y, CW - CM, y + 176), radius=30, fill=CARD2 if k == 0 else CARD,
                                outline=ORANGE if k == 0 else None, width=4)
            d.text((CM + 40, y + 40), h, font=F("b", 70), fill=ORANGE)
            d.text((CM + 230, y + 30), p, font=F("b", 58), fill=CREAM)
            d.text((CM + 230, y + 106), desc, font=F("r", 30), fill=MUTED)
            y += 194
        c_footer(d, i, n)
        return im
    return make


def c_cta(title="Zarezerwuj termin", sub="Wybierasz pakiet, dzień i godzinę. Płacisz online.", code=None):
    def make(i, n):
        im = Image.new("RGB", (CW, CH), BLACK); d = ImageDraw.Draw(im)
        if code:
            photo_card(im, code, CM, 80, CW - 2 * CM, 470)
            y = 620
        else:
            y = 300
        yy = paste_logo(im, CW / 2, y, 560)
        yy = text(d, CM, yy + 60, title, F("b", 76), CREAM, CW - 2 * CM, lh=1.08, center=True)
        yy = text(d, CM, yy + 12, sub, F("r", 36), MUTED, CW - 2 * CM, lh=1.32, center=True)
        cta_pill(d, CM, yy + 46, CW - 2 * CM)
        c_footer(d, i, n)
        return im
    return make


def render_carousel(slides, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = len(slides)
    paths = []
    for i, mk in enumerate(slides, 1):
        p = os.path.join(outdir, f"{i:02d}.jpg")
        mk(i, n).save(p, quality=92)
        paths.append(p)
    return paths


# ================= ROLKI 1080x1920 =================
FPS = 30


def r_scene(code, dur, kicker=None, title="", title2=None, sub=None, fx=None, cta=None):
    return dict(code=code, dur=dur, kicker=kicker, title=title, title2=title2, sub=sub, fx=fx, cta=cta)


def _layers(sc):
    """tło (czarne + logo) i warstwa tekstu dla sceny"""
    bg = Image.new("RGB", (SW, SH), BLACK)
    paste_logo(bg, SW / 2, 190, 300)
    tl = Image.new("RGBA", (SW, SH), (0, 0, 0, 0)); d = ImageDraw.Draw(tl)
    if sc["code"]:
        box = (SM, 360, SW - SM, 360 + 760)
        y = box[3] + 60
    else:
        box = None
        y = 760
    y = head_block(d, SM, y, SW - 2 * SM, sc["kicker"], sc["title"], sc["sub"], size=88, title2=sc["title2"])
    if sc["cta"]:
        cta_pill(d, SM, y + 46, SW - 2 * SM, sc["cta"])
    return bg, tl, box


def render_reel(scenes, path):
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", str(FPS),
           "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "medium",
           "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    prev = None
    for idx, sc in enumerate(scenes):
        bg, tl, box = _layers(sc)
        n = round(sc["dur"] * FPS)
        if box:
            bw, bh = box[2] - box[0], box[3] - box[1]
            big = cover(sc["code"], round(bw * 1.12), round(bh * 1.12), fx=sc["fx"])
            mask = rounded(Image.new("RGB", (bw, bh)), 40)
        last = None
        for f in range(n):
            t = f / max(1, n - 1)
            fr = bg.copy()
            if box:
                z = 1 + 0.10 * (t if idx % 2 == 0 else 1 - t)
                cw, ch = big.width / z, big.height / z
                x0, y0 = (big.width - cw) / 2, (big.height - ch) / 2
                ph = big.resize((bw, bh), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
                # wjazd karty
                a = min(1, f / (0.3 * FPS)); e = 1 - (1 - a) ** 3
                fr.paste(ph, (box[0], box[1] + round(30 * (1 - e))), mask)
            a = min(1, max(0, (f - 0.15 * FPS) / (0.35 * FPS))); e = 1 - (1 - a) ** 3
            if e > 0:
                o = tl if e >= 1 else tl.copy()
                if e < 1:
                    o.putalpha(o.getchannel("A").point(lambda v: round(v * e)))
                fr = fr.convert("RGBA"); fr.alpha_composite(o, (0, round(36 * (1 - e)))); fr = fr.convert("RGB")
            if prev is not None and f < 5:
                fr = Image.blend(prev, fr, (f + 1) / 6)
            p.stdin.write(fr.tobytes())
            last = fr
        prev = last
    p.stdin.close(); p.wait()
    return path
