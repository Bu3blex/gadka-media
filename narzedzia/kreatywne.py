"""Gadka studio v3: kreatywne, zróżnicowane formaty (od 13.10.2026).
Spójne są tylko: kolory z logo (czarny, krem, pomarańcz), fonty (Inter Display Black + Poppins) i logo.
Każdy post ma inny układ: plakat, paragon, czat, to-czy-to, polaroidy, checklista, duotone, wielka liczba, przekreślenia, ankieta.
Relacje 1080x1920, karuzele 1080x1350. Rolki: narzedzia/kinetyczne.py."""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design
from design import cover, gradient
from relacje_wyroznione import F, logo_rgba, wrap, text, BLACK, CARD, CARD2, CREAM, MUTED, ORANGE

design.FOCAL.update({"101": .27, "102": .55, "103": .45, "104": .5, "105": .35, "106": .45})
SITE = "gadkastudio.pl"
PAPER = (251, 247, 240)
INK = (14, 14, 14)
DIM = (120, 112, 104)
INTER = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
STORY = (1080, 1920)
POST = (1080, 1350)

_fc = {}


def FX(s, it=False):
    k = ("fx", s, it)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(INTER + ("InterDisplay-BlackItalic.otf" if it else "InterDisplay-Black.otf"), s)
    return _fc[k]


def FM(s, bold=True):
    return ImageFont.truetype(MONO + ("-Bold.ttf" if bold else ".ttf"), s)


def cap(f):
    b = f.getbbox("H")
    return b[3] - b[1]


def tw(f, t):
    return f.getlength(t)


# ---------------------------------------------------------------- logo
def logo_img(width, color=None):
    lg = logo_rgba()
    if color is not None:
        m = Image.new("RGBA", lg.size, color + (255,))
        m.putalpha(lg.getchannel("A"))
        lg = m
    return lg.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)


def put_logo(img, cx, y, width, color=None):
    lg = logo_img(width, color)
    img.paste(lg, (round(cx - width / 2), round(y)), lg)
    return y + lg.height


def is_light(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) > 140


def logo_for(img, cx, y, width, bg):
    """logo w kolorze dopasowanym do tła"""
    return put_logo(img, cx, y, width, BLACK if is_light(bg) or bg == ORANGE else None)


# ---------------------------------------------------------------- warstwy
def paste_layer(img, lay, x, y, shadow=0):
    x, y = round(x), round(y)
    if shadow:
        a = lay.getchannel("A").point(lambda v: v * 0.5)
        sh = Image.new("L", (lay.width + 80, lay.height + 80), 0)
        sh.paste(a, (40, 40))
        sh = sh.filter(ImageFilter.GaussianBlur(shadow))
        img.paste(Image.new("RGB", sh.size, (0, 0, 0)), (x - 40 + shadow // 2, y - 40 + shadow), sh)
    img.paste(lay, (x, y), lay)


def paste_center(img, lay, cx, cy, shadow=0):
    paste_layer(img, lay, cx - lay.width / 2, cy - lay.height / 2, shadow)


def grain(im, a=7, seed=3):
    arr = np.asarray(im).astype(np.int16)
    n = np.random.default_rng(seed).normal(0, a, arr.shape[:2])[..., None]
    return Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8))


def duotone(im, dark=BLACK, mid=ORANGE, light=CREAM):
    g = ImageOps.autocontrast(im.convert("L"), cutoff=1)
    return ImageOps.colorize(g, dark, light, mid=mid)


def photo(code, W, H, fx=None, zoom=1.0, duo=False, fy=.5):
    im = cover(code, W, H, zoom=zoom, fx=fx, fy=fy)
    return duotone(im) if duo else im


def shade(im, y0, y1, a0=0, a1=235, color=BLACK):
    return gradient(im, y0, y1, top_alpha=a0, bottom_alpha=a1, color=color)


def shade_top(im, h=420, a=200):
    g = Image.new("L", (1, h))
    for yy in range(h):
        g.putpixel((0, yy), round(a * (1 - yy / h) ** 1.6))
    im.paste(Image.new("RGB", (im.width, h), BLACK), (0, 0), g.resize((im.width, h)))
    return im


# ---------------------------------------------------------------- typografia
def fit(lines, maxw, maxsize, it=False, minsize=40):
    s = maxsize
    while s > minsize and any(tw(FX(s, it), (l[0] if isinstance(l, tuple) else l)) > maxw for l in lines):
        s -= 4
    return s


def mega(d, x, y, lines, size, fill=CREAM, it=False, step=1.3, align="l", w=1080, bg=None, stroke=6):
    """Wielka typografia. Linia: 'tekst' albo ('tekst', kolor) albo ('tekst', 'o', kolor_obrysu).
    y = góra wersalików pierwszej linii. Zwraca y dolnej krawędzi ostatniej linii."""
    f = FX(size, it); c = cap(f)
    for i, ln in enumerate(lines):
        t, col, o = (ln, fill, None) if not isinstance(ln, tuple) else (ln[0], ln[1], ln[2] if len(ln) > 2 else None)
        ww = tw(f, t)
        xx = x if align == "l" else (x + (w - ww) / 2 if align == "c" else x + w - ww)
        by = y + c + i * c * step
        if col == "o":
            d.text((xx, by), t, font=f, fill=bg, anchor="ls", stroke_width=stroke, stroke_fill=o)
        else:
            d.text((xx, by), t, font=f, fill=col, anchor="ls")
    return y + c + (len(lines) - 1) * c * step


def mega_h(lines, size, it=False, step=1.3):
    c = cap(FX(size, it))
    return c + (len(lines) - 1) * c * step


def body(d, x, y, t, size=42, fill=CREAM, w=900, center=False, weight="m", lh=1.3):
    return text(d, x, y, t, F(weight, size), fill, w, lh=lh, center=center)


def rich_body(img, x, y, t, size=42, fill=CREAM, w=900, center=False, weight="b", lh=1.3):
    d = ImageDraw.Draw(img); f = F(weight, size)
    for ln in wrap(d, t, f, w):
        xx = x + (w - d.textlength(ln, font=f)) / 2 if center else x
        rich(img, xx, y, ln, f, fill); y += round(size * lh)
    return y


def body_h(t, size=42, w=900, weight="m", lh=1.3):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    return len(wrap(d, t, F(weight, size), w)) * round(size * lh)


# ---------------------------------------------------------------- naklejki i ozdobniki
def sticker(t, size=46, bg=ORANGE, fg=BLACK, angle=-4, px=30, py=20, radius=16, font=None):
    f = font or FX(size)
    b = f.getbbox(t); c = cap(f)
    W_, H_ = round(tw(f, t) + 2 * px), round(c + 2 * py)
    lay = Image.new("RGBA", (W_ + 8, H_ + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((4, 4, 4 + W_, 4 + H_), radius=radius, fill=bg)
    d.text((4 + px, 4 + py + c), t, font=f, fill=fg, anchor="ls")
    return lay.rotate(angle, resample=Image.BICUBIC, expand=True)


def emoji(ch, size=120, angle=0):
    f = ImageFont.truetype(EMOJI, 109)
    lay = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((8, 8), ch, font=f, embedded_color=True)
    lay = lay.crop(lay.getbbox())
    lay = lay.resize((size, round(lay.height * size / lay.width)), Image.LANCZOS)
    return lay.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else lay


def marker(lines, size, bg=ORANGE, fg=BLACK, angle=-3, it=True, px=26, py=18, gap=12, align="l"):
    """nagłówek na blokach jak zakreślacz; linia: 'tekst' albo ('tekst', bg, fg)"""
    f = FX(size, it); c = cap(f)
    specs = [(l, bg, fg) if not isinstance(l, tuple) else l for l in lines]
    widths = [tw(f, s[0]) + 2 * px for s in specs]
    Wm = round(max(widths)) + 20; bh = c + 2 * py
    lay = Image.new("RGBA", (Wm, round(len(specs) * (bh + gap))), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, (t, b_, f_) in enumerate(specs):
        x0 = 0 if align == "l" else (Wm - widths[i]) / 2
        y0 = i * (bh + gap)
        d.rectangle((x0, y0, x0 + widths[i], y0 + bh), fill=b_)
        d.text((x0 + px, y0 + py + c), t, font=f, fill=f_, anchor="ls")
    return lay.rotate(angle, resample=Image.BICUBIC, expand=True)


def polaroid(code, w, h, angle=0, caption=None, fx=None, tape=True, duo=False):
    bd = 22; bot = 96 if caption else bd
    lay = Image.new("RGBA", (w + 2 * bd, h + bd + bot), PAPER + (255,))
    lay.paste(photo(code, w, h, fx=fx, duo=duo), (bd, bd))
    d = ImageDraw.Draw(lay)
    if caption:
        f = F("b", 38)
        d.text(((w + 2 * bd) / 2, h + bd + bot / 2 + 4), caption, font=f, fill=INK, anchor="mm")
    if tape:
        tp = Image.new("RGBA", (190, 54), (255, 236, 200, 170))
        tp = tp.rotate(-6, expand=True, resample=Image.BICUBIC)
        canvas = Image.new("RGBA", (lay.width, lay.height + 30), (0, 0, 0, 0))
        canvas.paste(lay, (0, 30))
        canvas.alpha_composite(tp, (round(lay.width / 2 - tp.width / 2), 0))
        lay = canvas
    return lay.rotate(angle, resample=Image.BICUBIC, expand=True)


def band(t, angle=-6, bg=ORANGE, fg=BLACK, size=52, h=104, length=2600):
    f = FX(size); unit = t.upper() + "   •   "
    strip = Image.new("RGBA", (length, h), bg + (255,)); d = ImageDraw.Draw(strip)
    x = -40; c = cap(f)
    while x < length:
        d.text((x, h / 2 + c / 2), unit, font=f, fill=fg, anchor="ls"); x += tw(f, unit)
    return strip.rotate(angle, resample=Image.BICUBIC, expand=True)


def arrow(d, x, y, length=90, color=BLACK, w=10):
    d.line((x, y, x + length, y), fill=color, width=w)
    d.polygon([(x + length + 6, y), (x + length - 26, y - 24), (x + length - 26, y + 24)], fill=color)


def tick(d, cx, cy, s, color=ORANGE, w=12):
    d.line([(cx - s * .45, cy), (cx - s * .12, cy + s * .33), (cx + s * .48, cy - s * .38)], fill=color, width=w, joint="curve")


def cross(d, cx, cy, s, color=ORANGE, w=12):
    d.line([(cx - s * .38, cy - s * .38), (cx + s * .38, cy + s * .38)], fill=color, width=w)
    d.line([(cx - s * .38, cy + s * .38), (cx + s * .38, cy - s * .38)], fill=color, width=w)


def receipt(rows, total, w=760, title="GADKA STUDIO", sub="ul. Chełmżyńska 10E, Warszawa", note="DZIĘKUJEMY ZA GADKĘ :)", angle=2, total_label="RAZEM"):
    fr, fb, ft = FM(38, False), FM(40), FX(78)
    pad = 54; lh = 64
    h = 70 + 90 + 50 + 40 + len(rows) * lh + 40 + 110 + 40 + 120 + 60 + 50
    lay = Image.new("RGBA", (w, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    z = 20  # ząbki
    pts = [(0, z)] + [(x, 0 if (x // z) % 2 else z) for x in range(0, w + 1, z)] + [(w, z), (w, h + 20)]
    pts += [(x, h + 20 - (0 if (x // z) % 2 else z)) for x in range(w, -1, -z)] + [(0, h + 20)]
    d.polygon(pts, fill=PAPER)
    y = 70
    lg = logo_img(300, BLACK); lay.paste(lg, (round(w / 2 - 150), y), lg); y += lg.height + 26
    d.text((w / 2, y), sub, font=FM(26, False), fill=DIM, anchor="mt"); y += 50
    dash = "- " * 40
    d.text((pad, y), dash, font=fr, fill=DIM); y += 46
    for name, price in rows:
        d.text((pad, y), name, font=fb if price != "0 zł" else fr, fill=INK)
        d.text((w - pad, y), price, font=fb, fill=ORANGE if price == "0 zł" else INK, anchor="ra")
        y += lh
    d.text((pad, y), dash, font=fr, fill=DIM); y += 56
    c = cap(ft)
    d.text((pad, y + c), total_label, font=ft, fill=INK, anchor="ls")
    d.text((w - pad, y + c), total, font=ft, fill=ORANGE, anchor="rs"); y += c + 50
    rnd = random.Random(7); x = pad
    while x < w - pad - 8:
        bw = rnd.choice([3, 4, 6, 9]); d.rectangle((x, y, x + bw, y + 100), fill=INK); x += bw + rnd.choice([4, 6, 8])
    y += 130
    d.text((w / 2, y), note, font=FM(30), fill=INK, anchor="mt")
    return lay.rotate(angle, resample=Image.BICUBIC, expand=True)


def _is_emo(ch):
    return ord(ch) >= 0x2600 and not (0x2190 <= ord(ch) <= 0x21FF) or ch in "\ufe0f\u200d"


def rich(img, x, y, t, f, fill):
    """tekst z emoji (emoji z NotoColorEmoji); y = góra linii"""
    d = ImageDraw.Draw(img); segs = []; cur = ""; emo = False
    for ch in t:
        e = _is_emo(ch)
        if e != emo and cur:
            segs.append((cur, emo)); cur = ""
        cur += ch; emo = e
    if cur: segs.append((cur, emo))
    for seg, e in segs:
        if e:
            for cl in [c for c in seg if c not in "\ufe0f\u200d"]:
                em = emoji(cl, round(f.size * 1.05))
                img.paste(em, (round(x), round(y + f.size * 0.18)), em); x += em.width + 6
        else:
            d.text((x, y), seg, font=f, fill=fill); x += f.getlength(seg)
    return x


def chat_layer(msgs, w=900, size=44, name="Współprowadzący", sub="online"):
    """czat z dymkami; msgs: [('l'|'r', tekst)]"""
    f = F("m", size); dd = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    maxw = round(w * 0.76); lh = round(size * 1.3); px, py = 36, 26
    bubbles = []
    for side, t in msgs:
        lines = wrap(dd, t, f, maxw - 2 * px)
        bw = max(dd.textlength(l, font=f) for l in lines) + 2 * px
        bubbles.append((side, lines, bw, len(lines) * lh + 2 * py - 6))
    head = 150
    H_ = head + sum(b[3] + 22 for b in bubbles) + 40
    lay = Image.new("RGBA", (w, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w, H_), radius=44, fill=(24, 24, 24))
    d.ellipse((34, 34, 116, 116), fill=ORANGE)
    d.text((75, 76), name[0], font=FX(44), fill=BLACK, anchor="mm")
    d.text((140, 40), name, font=F("b", 38), fill=CREAM)
    d.text((140, 88), sub, font=F("r", 28), fill=(120, 200, 120))
    d.line((0, head - 10, w, head - 10), fill=(44, 44, 44), width=2)
    y = head + 20
    for side, lines, bw, bh in bubbles:
        x0 = 30 if side == "l" else w - 30 - bw
        d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=36, fill=CARD2 if side == "l" else ORANGE)
        yy = y + py - 4
        for l in lines:
            rich(lay, x0 + px, yy, l, f, CREAM if side == "l" else BLACK); yy += lh
        y += bh + 22
    return lay


# ---------------------------------------------------------------- karuzela: stopka
def footer(im, i, n, swipe=False):
    d = ImageDraw.Draw(im); W, H = im.size
    reg = im.crop((0, H - 120, W, H)).convert("L")
    light = np.asarray(reg).mean() > 130
    col = INK if light else CREAM
    f = F("b", 28)
    d.text((70, H - 66), SITE, font=f, fill=col, anchor="lm")
    if swipe:
        st = sticker("PRZESUŃ", 34, bg=ORANGE if light or True else ORANGE, fg=BLACK, angle=0, px=24, py=14, radius=30)
        x0 = W - 70 - st.width - 70
        paste_layer(im, st, x0, H - 66 - st.height / 2)
        arrow(d, W - 70 - 60, H - 66, 50, col, 8)
    else:
        t = f"{i}/{n}"
        d.text((W - 70, H - 66), t, font=f, fill=col, anchor="rm")
    return im


# ================================================================ SZABLONY (działają w 1080x1920 i 1080x1350)
def _frame(size):
    W, H = size
    story = H > 1500
    top = 150 if story else 60          # logo
    lo = 1600 if story else H - 130     # dolna granica treści
    return W, H, story, top, lo


def t_poster(lines, bg=ORANGE, fg=BLACK, sub=None, stick=None, emo=None, it=False, band_t=None, maxsize=250, size=STORY, sub_col=None, accent=None):
    """plakat: wielka typografia na kolorze"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 230 if story else 190, bg)
    s = fit(lines, W - 150, maxsize, it)
    mh = mega_h(lines, s, it)
    sh = (body_h(sub, 44 if story else 38, W - 160) + 40) if sub else 0
    y = (top + 140 + (lo - (220 if band_t else 0)) - mh - sh) / 2
    y = mega(d, 75, y, lines, s, fg, it=it, bg=bg)
    if sub:
        body(d, 80, y + 50, sub, 44 if story else 38, sub_col or (INK if is_light(bg) or bg == ORANGE else MUTED), W - 160, weight="m")
    if stick:
        st = sticker(stick, 44 if story else 38, bg=accent or (BLACK if bg == ORANGE else ORANGE), fg=CREAM if bg == ORANGE else BLACK, angle=5)
        paste_layer(im, st, W - st.width - 50, (y - mh) - st.height - 10, shadow=10)
    if emo:
        e = emoji(emo, 150 if story else 120, angle=12)
        paste_layer(im, e, W - e.width - 60, lo - e.height - (240 if band_t else 30))
    if band_t:
        b = band(band_t, -5, bg=BLACK if bg != BLACK else ORANGE, fg=CREAM if bg != BLACK else BLACK)
        paste_center(im, b, W / 2, lo - 90)
    return grain(im, 5)


def t_photo(code, lines, sub=None, stick=None, emo=None, duo=False, fx=None, size=STORY, msize=96, pos="low", angle=-3, mbg=ORANGE, mfg=BLACK):
    """zdjęcie na cały kadr + nagłówek na blokach zakreślacza"""
    W, H, story, top, lo = _frame(size)
    im = photo(code, W, H, fx=fx, duo=duo)
    lay = marker(lines, msize, bg=mbg, fg=mfg, angle=angle)
    sh = (body_h(sub, 42, W - 160) + 30) if sub else 0
    if pos == "low":
        y = lo - sh - lay.height
        im = shade(im, y - 400, y + 200, 0, 225)
    else:
        y = top + (260 if story else 180)
        im = shade(im, lo - 300, H, 0, 160)
    shade_top(im, 380 if story else 300, 190)
    d = ImageDraw.Draw(im)
    put_logo(im, W / 2, top, 230 if story else 190)
    paste_layer(im, lay, 50, y, shadow=14)
    if sub:
        body(d, 80, y + lay.height + 20, sub, 42, CREAM, W - 160, weight="m")
    if stick:
        st = sticker(stick, 42, bg=CREAM, fg=BLACK, angle=6)
        paste_layer(im, st, W - st.width - 50, y - st.height - 30, shadow=10)
    if emo:
        e = emoji(emo, 140, angle=-10)
        paste_layer(im, e, W - e.width - 70, y - e.height - 20 - (90 if stick else 0))
    return grain(im, 5)


def t_receipt(hook, rows, total, sub=None, stick=None, size=STORY, bg=BLACK, total_label="RAZEM"):
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 230 if story else 170, bg)
    s = fit(hook, W - 160, 120 if story else 92)
    y = mega(d, 80, top + (200 if story else 120), hook, s, CREAM, bg=bg, align="c", w=W - 160)
    rc = receipt(rows, total, w=860 if story else 700, angle=2.5, total_label=total_label)
    if not story:
        rc = rc.resize((round(rc.width * 0.86), round(rc.height * 0.86)), Image.LANCZOS)
    paste_center(im, rc, W / 2, y + 60 + rc.height / 2, shadow=24)
    if stick:
        st = sticker(stick, 42, angle=-8)
        paste_layer(im, st, 40, y + 40 + rc.height * 0.62, shadow=10)
    if sub:
        body(d, 80, lo - 60, sub, 38, MUTED, W - 160, center=True)
    return grain(im, 4)


def t_chat(msgs, title=None, footer_t=None, name="Współprowadzący", size=STORY, bg=ORANGE, stick=None):
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 230 if story else 170, bg)
    y = top + (170 if story else 100)
    if title:
        s = fit(title, W - 160, 110 if story else 104)
        y = mega(d, 80, y, title, s, BLACK if bg == ORANGE else CREAM, bg=bg) + 50
    ch = chat_layer(msgs, w=W - 120, size=52 if story else 48, name=name)
    fh = (body_h(footer_t, 46, W - 160, "b") + 50) if footer_t else 0
    y = max(y, (y + lo - ch.height - fh) / 2)
    paste_layer(im, ch, 60, y, shadow=18)
    y += ch.height
    if footer_t:
        rich_body(im, 80, y + 50, footer_t, 46 if story else 34, BLACK if bg == ORANGE else CREAM, W - 160, center=True, weight="b")
    if stick:
        st = sticker(stick, 40, bg=BLACK if bg == ORANGE else ORANGE, fg=CREAM if bg == ORANGE else BLACK, angle=-6)
        paste_layer(im, st, W - st.width - 40, y - 40, shadow=10)
    return grain(im, 4)


def t_split(a, b, la, lb, q, size=STORY, sub=None):
    """to czy to: dwa zdjęcia, pytanie na pasku, etykiety A/B"""
    W, H, story, top, lo = _frame(size)
    mid = H // 2
    im = Image.new("RGB", size, BLACK)
    im.paste(photo(a[0], W, mid - 6, fx=a[1] if len(a) > 1 else None), (0, 0))
    im.paste(photo(b[0], W, H - mid - 6, fx=b[1] if len(b) > 1 else None), (0, mid + 6))
    shade_top(im, 380 if story else 260, 190)
    put_logo(im, W / 2, top, 230 if story else 170)
    d = ImageDraw.Draw(im)
    for (lab, txt), cy in ((("A", la), mid * 0.62), (("B", lb), mid + (H - mid) * 0.40)):
        r = 78 if story else 62
        d.ellipse((70, cy - r, 70 + 2 * r, cy + r), fill=ORANGE)
        d.text((70 + r, cy + 4), lab, font=FX(96 if story else 76), fill=BLACK, anchor="mm")
        st = sticker(txt, 44 if story else 36, bg=CREAM, fg=BLACK, angle=0, px=26, py=16)
        paste_layer(im, st, 70 + 2 * r + 24, cy - st.height / 2, shadow=10)
    bd = marker([q], 92 if story else 74, bg=ORANGE, fg=BLACK, angle=-3, align="c")
    paste_center(im, bd, W / 2, mid, shadow=16)
    if sub:
        st = sticker(sub, 38, bg=BLACK, fg=CREAM, angle=3, px=26, py=16)
        paste_center(im, st, W / 2, mid + bd.height / 2 + 50, shadow=8)
    return grain(im, 4)


def t_bignum(code, num, lines, sub=None, size=STORY, fx=None, duo=True, numsize=None, stick=None):
    """wielka liczba w obrysie na zdjęciu"""
    W, H, story, top, lo = _frame(size)
    im = photo(code, W, H, fx=fx, duo=duo)
    im = shade(im, int(H * 0.35), int(H * 0.8), 40, 230)
    shade_top(im, 380, 200)
    put_logo(im, W / 2, top, 230 if story else 170)
    lay = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ns = numsize or fit([num], W - 60, 640 if story else 460)
    f = FX(ns, True)
    ny = H * (0.47 if story else 0.5)
    d.text((W / 2, ny), num, font=f, fill=(0, 0, 0, 0), anchor="ms", stroke_width=8, stroke_fill=CREAM)
    im.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(im)
    s = fit(lines, W - 160, 110 if story else 84)
    y = mega(d, 80, ny + 60, lines, s, CREAM, bg=BLACK, align="c", w=W - 160)
    if sub:
        body(d, 80, y + 40, sub, 42 if story else 34, CREAM, W - 160, center=True)
    if stick:
        st = sticker(stick, 42, angle=8)
        paste_layer(im, st, W - st.width - 60, ny - ns * 0.85, shadow=10)
    return grain(im, 5)


def t_check(title, items, sub=None, bg=CREAM, size=STORY, stick=None, emo=None):
    """checklista z ręcznymi ptaszkami/krzyżykami; items: [(tekst, True/False)]"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    fg = INK if is_light(bg) else CREAM
    logo_for(im, W / 2, top, 230 if story else 170, bg)
    s = fit(title, W - 160, 150 if story else 130)
    ih = (150 if story else 118)
    total = mega_h(title, s) + 70 + len(items) * ih + ((body_h(sub, 40, W - 160) + 40) if sub else 0)
    y = max(top + 170, (top + 120 + lo - total) / 2)
    y = mega(d, 80, y, title, s, fg, bg=bg) + 70
    fi = F("b", 62 if story else 56)
    for t, ok in items:
        bx = 80; bs = 86 if story else 76
        d.rounded_rectangle((bx, y, bx + bs, y + bs), radius=12, outline=fg, width=6)
        (tick if ok else cross)(d, bx + bs / 2 + 6, y + bs / 2 - 4, bs * 1.25, ORANGE, 13)
        d.text((bx + bs + 34, y + bs / 2), t, font=fi, fill=fg if ok else DIM, anchor="lm")
        if not ok:
            l = fi.getlength(t)
            d.line((bx + bs + 30, y + bs / 2 + 2, bx + bs + 38 + l, y + bs / 2 + 2), fill=ORANGE, width=7)
        y += ih
    if sub:
        body(d, 80, y + 30, sub, 40 if story else 34, fg, W - 160, weight="m")
    if stick:
        st = sticker(stick, 42, bg=ORANGE, fg=BLACK, angle=-6)
        paste_layer(im, st, W - st.width - 50, top + 120, shadow=8)
    if emo:
        e = emoji(emo, 150, 10); paste_layer(im, e, W - e.width - 70, lo - e.height)
    return grain(im, 4)


def t_meme(rows, code, punch=None, size=STORY, fx=None, bg=BLACK):
    """format mema: 'Nikt:' / 'Ja:' + zdjęcie"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 220 if story else 160, bg)
    y = top + (170 if story else 100)
    for who, what in rows:
        f1 = F("b", 52 if story else 42)
        d.text((80, y), who, font=f1, fill=ORANGE)
        x2 = 80 + f1.getlength(who) + 20
        y = text(d, x2, y, what, F("m", 52 if story else 42), CREAM, W - 80 - x2, lh=1.25) + (26 if story else 16)
    ph_h = (lo - y - (230 if punch else 60)) if story else (lo - y - (170 if punch else 40))
    ph = photo(code, W - 160, max(300, int(ph_h)), fx=fx)
    m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width, ph.height), radius=36, fill=255)
    im.paste(ph, (80, round(y + 20)), m)
    if punch:
        mk = marker([punch], 76 if story else 60, angle=-3, align="c")
        paste_center(im, mk, W / 2, y + 20 + ph.height, shadow=14)
    return grain(im, 4)


def t_vs(top_title, bad, code, good_title, good, size=STORY, fx=None):
    """VS: górna połowa czarna z krzyżykami, dolna zdjęcie z ptaszkami"""
    W, H, story, top, lo = _frame(size)
    mid = int(H * (0.47 if story else 0.46))
    im = Image.new("RGB", size, (20, 20, 20))
    ph = photo(code, W, H - mid, fx=fx)
    ph = shade(ph, int((H - mid) * 0.25), H - mid, 30, 225)
    im.paste(ph, (0, mid))
    d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 220 if story else 160, BLACK)
    fsz = 100 if story else 84
    y = top + (190 if story else 95)
    mega(d, 80, y, [top_title], fit([top_title], W - 160, fsz), DIM, bg=BLACK)
    y += cap(FX(fsz)) + (44 if story else 30)
    fi = F("m", 52 if story else 46)
    for t in bad:
        cross(d, 105, y + 26, 46, ORANGE, 10)
        d.text((150, y + 26), t, font=fi, fill=MUTED, anchor="lm"); y += 90 if story else 70
    yy = H - (330 if story else 110) - len(good) * (90 if story else 70)
    mega(d, 80, yy - (130 if story else 100), [good_title], fit([good_title], W - 160, fsz + 10), CREAM, bg=BLACK)
    fi2 = F("b", 54 if story else 48)
    for t in good:
        tick(d, 105, yy + 26, 54, ORANGE, 11)
        d.text((150, yy + 26), t, font=fi2, fill=CREAM, anchor="lm"); yy += 90 if story else 70
    r = 84 if story else 66
    d.ellipse((W / 2 - r, mid - r, W / 2 + r, mid + r), fill=ORANGE)
    d.text((W / 2, mid + 4), "VS", font=FX(80 if story else 62, True), fill=BLACK, anchor="mm")
    return grain(im, 4)


def t_polaroids(title, cards_, sub=None, bg=CREAM, size=STORY, stick=None):
    """kremowe tło, rozrzucone polaroidy z podpisami; cards_: [(kod, podpis)]"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 230 if story else 170, bg)
    s = fit(title, W - 160, 118 if story else 86)
    y = mega(d, 80, top + (170 if story else 100), title, s, INK, bg=bg, align="c", w=W - 160)
    if sub:
        y = body(d, 80, y + 30, sub, 40 if story else 32, DIM, W - 160, center=True)
    n = len(cards_)
    if story:
        spots = {1: [(540, 1180, 4)], 2: [(380, 1000, -6), (700, 1330, 5)], 3: [(330, 960, -7), (750, 1060, 6), (520, 1420, -2)]}[n]
        pw, ph_ = (560, 420) if n > 1 else (820, 620)
    else:
        spots = {1: [(540, 820, 3)], 2: [(330, 840, -6), (760, 900, 5)], 3: [(250, 860, -7), (560, 930, 4), (850, 850, -4)]}[n]
        pw, ph_ = {1: (720, 500), 2: (450, 360), 3: (330, 300)}[n]
    for (code, capt), (cx, cy, ang) in zip(cards_, spots):
        p = polaroid(code, pw, ph_, ang, capt)
        paste_center(im, p, cx, cy, shadow=18)
    if stick:
        st = sticker(stick, 42, angle=-7)
        paste_layer(im, st, 60, lo - st.height - (20 if story else 0), shadow=8)
    return grain(im, 4)


def t_poll(q, options, hint=None, bg=BLACK, size=STORY, hl=None):
    """jak ankieta z IG: pytanie + paski opcji (bez wyników)"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 230 if story else 170, bg)
    fg = INK if is_light(bg) else CREAM
    s = fit(q, W - 160, 118 if story else 88)
    oh = 150 if story else 118
    total = mega_h(q, s) + 80 + len(options) * (oh + 24)
    y = max(top + 170, (top + 140 + lo - total) / 2)
    y = mega(d, 80, y, q, s, fg, bg=bg, align="c", w=W - 160) + 80
    for i, (a, b_) in enumerate(options):
        on = (i == hl)
        d.rounded_rectangle((80, y, W - 80, y + oh), radius=oh // 2, fill=ORANGE if on else (CARD2 if not is_light(bg) else (235, 222, 210)))
        d.text((140, y + oh / 2), a, font=FX(64 if story else 52), fill=BLACK if on else fg, anchor="lm")
        d.text((W - 140, y + oh / 2), b_, font=F("b", 40 if story else 34), fill=BLACK if on else (MUTED if not is_light(bg) else DIM), anchor="rm")
        y += oh + 24
    if hint:
        rich_body(im, 80, y + 30, hint, 40 if story else 34, MUTED if not is_light(bg) else DIM, W - 160, center=True, weight="m")
    return grain(im, 4)


def t_strike(title, struck, final, sub=None, bg=BLACK, size=STORY, code=None):
    """lista przekreśleń + puenta"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg)
    if code:
        im = shade(photo(code, W, H, duo=True), 0, H, 200, 200)
    d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 230 if story else 170, bg)
    y = top + (190 if story else 110)
    s = fit(title, W - 160, 110 if story else 100)
    y = mega(d, 80, y + (120 if story else 60), title, s, CREAM, bg=bg) + (60 if story else 40)
    f = F("b", 80 if story else 72)
    for t in struck:
        d.text((80, y), t, font=f, fill=MUTED)
        l = f.getlength(t); mid = y + f.size * 0.62
        d.line((70, mid + 6, 90 + l, mid - 6), fill=ORANGE, width=12)
        y += round(f.size * 1.45)
    mk = marker(final, 120 if story else 106, angle=-3)
    paste_layer(im, mk, 50, y + 30, shadow=14)
    if sub:
        body(d, 80, y + 50 + mk.height, sub, 42 if story else 34, CREAM, W - 160)
    return grain(im, 5)


def t_cta(title, sub=None, code=None, size=STORY, bg=ORANGE, stick=None):
    """ostatni slajd/plansza: rezerwacja"""
    W, H, story, top, lo = _frame(size)
    if code:
        im = duotone(photo(code, W, H)) if bg == ORANGE else photo(code, W, H)
        im = shade(im, 0, H, 150, 150, color=BLACK)
    else:
        im = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(im)
    base = BLACK if code else bg
    y = H * (0.28 if story else 0.2)
    y = logo_for(im, W / 2, y, 620 if story else 520, base)
    s = fit(title, W - 160, 110 if story else 90)
    fg = BLACK if (base == ORANGE or is_light(base)) else CREAM
    y = mega(d, 80, y + 90, title, s, fg, bg=base, align="c", w=W - 160)
    if sub:
        y = body(d, 80, y + 36, sub, 40 if story else 34, fg, W - 160, center=True)
    st = sticker("REZERWACJA: " + SITE.upper(), 46 if story else 40, bg=BLACK if base == ORANGE else ORANGE, fg=CREAM if base == ORANGE else BLACK, angle=-3, px=36, py=24, radius=50)
    paste_center(im, st, W / 2, y + 70 + st.height / 2, shadow=10)
    if stick:
        s2 = sticker(stick, 38, bg=CREAM, fg=BLACK, angle=7)
        paste_layer(im, s2, W - s2.width - 60, y + 140 + st.height, shadow=8)
    return grain(im, 4)


def t_grid(codes, title, size=POST, labels=None):
    """kolaż 2x2 zdjęć + nagłówek na środku"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, BLACK)
    g = 8; cw, ch = (W - g) // 2, (H - g) // 2
    for k, c in enumerate(codes[:4]):
        x, y = (k % 2) * (cw + g), (k // 2) * (ch + g)
        im.paste(photo(c, cw, ch), (x, y))
        if labels:
            st = sticker(labels[k], 34, bg=CREAM, fg=BLACK, angle=0, px=18, py=12, radius=10)
            paste_layer(im, st, x + 24, y + 24 + (110 if k < 2 else 0))
    mk = marker(title, 96, angle=-4, align="c")
    paste_center(im, mk, W / 2, H / 2, shadow=18)
    put_logo(im, W / 2, 40, 170)
    return grain(im, 4)


def t_ticket(hours, price, what, bg=BLACK, size=POST, note="cena brutto"):
    """bilet z ceną pakietu"""
    W, H, story, top, lo = _frame(size)
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    logo_for(im, W / 2, top, 170, bg)
    tw_, th_ = W - 160, 760
    lay = Image.new("RGBA", (tw_, th_), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((0, 0, tw_, th_), radius=40, fill=ORANGE)
    for cy in (th_ * 0.58,):
        dd.ellipse((-40, cy - 40, 40, cy + 40), fill=(0, 0, 0, 0)); dd.ellipse((tw_ - 40, cy - 40, tw_ + 40, cy + 40), fill=(0, 0, 0, 0))
        for x in range(60, tw_ - 60, 34):
            dd.line((x, cy, x + 16, cy), fill=BLACK, width=4)
    dd.text((60, 60), "BILET DO STUDIA", font=FM(34), fill=BLACK)
    dd.text((60, 120 + cap(FX(260, True))), hours, font=FX(260, True), fill=BLACK, anchor="ls")
    dd.text((tw_ - 60, 120 + cap(FX(110))), price, font=FX(110), fill=CREAM, anchor="rs")
    text(dd, 60, th_ * 0.58 + 50, what, F("b", 44), BLACK, tw_ - 120, lh=1.25)
    dd.text((60, th_ - 70), note.upper(), font=FM(28), fill=BLACK)
    lay = lay.rotate(-3, resample=Image.BICUBIC, expand=True)
    paste_center(im, lay, W / 2, H / 2 + 20, shadow=22)
    return grain(im, 4)


# ---------------------------------------------------------------- karuzele
def slide(fn, *a, **k):
    """slajd karuzeli: fn(..., size=POST) + stopka"""
    def make(i, n):
        k2 = dict(k); k2.setdefault("size", POST)
        return footer(fn(*a, **k2), i, n, swipe=(i == 1))
    return make


def render_carousel(slides, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = len(slides); out = []
    for i, mk in enumerate(slides, 1):
        p = os.path.join(outdir, f"{i:02d}.jpg"); mk(i, n).convert("RGB").save(p, quality=92); out.append(p)
    return out
