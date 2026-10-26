#!/usr/bin/env bash
# Użycie: bash przygotuj.sh <folder_rolki>
# Tworzy folder roboczy z szablonem, fontami, logo, zdjęciami studia i teksturą szumu.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$SRC/../../.." && pwd)"
DST="$1"; [ -z "$DST" ] && { echo "podaj folder"; exit 1; }
mkdir -p "$DST/img" "$DST/fonts" "$DST/klipy"
cp "$SRC/index.html" "$SRC/anim.js" "$SRC/render.py" "$SRC/klip.sh" "$DST/" 2>/dev/null || true
for w in Thin Light SemiBold Bold ExtraBold Black BlackItalic; do cp "/usr/share/fonts/opentype/inter/InterDisplay-$w.otf" "$DST/fonts/" 2>/dev/null || true; done
cp "$REPO/marka/logo_kremowe_przezroczyste.png" "$DST/logo.png"; cp "$REPO/marka/logo_czarne_przezroczyste.png" "$DST/logo_black.png"
python3 - "$REPO/zrodla" "$DST/img" <<'PY'
import sys, os, re
from PIL import Image
import numpy as np
src, dst = sys.argv[1], sys.argv[2]
for f in sorted(os.listdir(src)):
    m = re.search(r"P1160(\d{3})", f)
    if not m: continue
    im = Image.open(os.path.join(src, f)).convert("RGB"); im.thumbnail((1800, 1800)); im.save(os.path.join(dst, m.group(1) + ".jpg"), quality=90)
Image.fromarray((np.random.default_rng(1).random((600, 600)) * 255).astype("uint8")).save(os.path.join(dst, "noise.png"))
PY
echo "gotowe: $DST (zdjęcia img/001.jpg … img/106.jpg)"
