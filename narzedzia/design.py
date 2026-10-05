from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, re

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zrodla")
FD = "/usr/share/fonts/opentype/inter/"
NAVY = (11, 27, 46)
ORANGE = (242, 118, 46)
CREAM = (246, 241, 234)
WHITE = (255, 255, 255)

# focal point (x share) for each photo, used for vertical crops
FOCAL = {"001": .5, "004": .5, "007": .5, "010": .5, "013": .27, "016": .45, "019": .33,
         "022": .5, "025": .5, "028": .55, "031": .42, "034": .42, "037": .62, "041": .3,
         "044": .45, "047": .55, "050": .42, "053": .42, "056": .55, "059": .62}


def font(w, size):
    names = {"black": "InterDisplay-Black.otf", "xbold": "InterDisplay-ExtraBold.otf",
             "bold": "InterDisplay-Bold.otf", "semi": "InterDisplay-SemiBold.otf",
             "med": "InterDisplay-Medium.otf"}
    p = FD + names[w]
    if not os.path.exists(p):
        p = FD + "InterDisplay-Bold.otf"
    return ImageFont.truetype(p, size)


_cache = {}


def photo(code):
    if code not in _cache:
        f = [x for x in os.listdir(SRC) if f"P1160{code}" in x][0]
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        im.thumbnail((3000, 3000))
        _cache[code] = im
    return _cache[code]


def cover(code, W, H, zoom=1.0, fx=None, fy=.5):
    im = photo(code)
    fx = FOCAL.get(code, .5) if fx is None else fx
    s = max(W / im.width, H / im.height) * zoom
    r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(round(r.width * fx - W / 2), 0), r.width - W)
    y = min(max(round(r.height * fy - H / 2), 0), r.height - H)
    out = r.crop((x, y, x + W, y + H))
    return ImageEnhance.Contrast(out).enhance(1.04)


def gradient(img, start, end, top_alpha=0, bottom_alpha=235, color=NAVY):
    W, H = img.size
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        if y < start:
            a = top_alpha
        elif y > end:
            a = bottom_alpha
        else:
            t = (y - start) / max(1, end - start)
            t = t * t * (3 - 2 * t)
            a = round(top_alpha + (bottom_alpha - top_alpha) * t)
        g.putpixel((0, y), a)
    mask = g.resize((W, H))
    layer = Image.new("RGB", (W, H), color)
    return Image.composite(layer, img, mask)


def nbsp(text):
    # Polish typography: keep 1-letter words and numbers with the next word
    return re.sub(r"(?<![\w\u00a0])(\w|\d+[×x]?) ", lambda m: m.group(1) + "\u00a0", text)


def wrap(draw, text, f, maxw):
    text = nbsp(text)
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, f, fill, maxw, lh=1.08, anchor_bottom=False, hl=None):
    lines = wrap(draw, text, f, maxw)
    step = round(f.size * lh)
    if anchor_bottom:
        y = y - step * len(lines)
    for ln in lines:
        hlx = nbsp(hl) if hl else None
        if hlx and hlx not in ln and hl in ln:
            hlx = hl
        if hlx and hlx in ln:
            hl = hlx
            pre, post = ln.split(hl, 1)
            cx = x
            draw.text((cx, y), pre, font=f, fill=fill); cx += draw.textlength(pre, font=f)
            draw.text((cx, y), hl, font=f, fill=ORANGE); cx += draw.textlength(hl, font=f)
            draw.text((cx, y), post, font=f, fill=fill)
        else:
            draw.text((x, y), ln, font=f, fill=fill)
        y += step
    return y


def pill(draw, x, y, text, f, bg=ORANGE, fg=WHITE, padx=28, pady=16, right=False):
    w = draw.textlength(text, font=f)
    asc, desc = f.getmetrics()
    h = asc + pady * 2
    if right:
        x = x - (w + padx * 2)
    draw.rounded_rectangle((x, y, x + w + padx * 2, y + h), radius=h // 2, fill=bg)
    draw.text((x + padx, y + pady - 2), text, font=f, fill=fg)
    return x + w + padx * 2, y + h


def wordmark(draw, x, y, size=34, fill=WHITE, right=False, bg=NAVY):
    f1, f2 = font("black", size), font("med", size)
    w = draw.textlength("gadka", font=f1) + draw.textlength(" studio", font=f2)
    if right:
        x -= w
    if bg:
        asc, _ = f1.getmetrics()
        draw.rounded_rectangle((x - 22, y - 12, x + w + 22, y + asc + 14), radius=(asc + 26) // 2, fill=bg)
    draw.text((x, y), "gadka", font=f1, fill=fill)
    draw.text((x + draw.textlength("gadka", font=f1), y), " studio", font=f2, fill=ORANGE)
