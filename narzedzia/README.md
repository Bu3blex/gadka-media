# Generator mediów Gadka studio

- `zrodla/` – oryginalne zdjęcia studia (kody kadrów = 3 ostatnie cyfry, np. `041`).
- `design.py` – paleta (granat, pomarańcz, krem), font Inter Display, kadrowanie, znak „gadka studio”.
- `stories.py` → `story(data, kadr, kicker, nagłówek, wyróżnienie, podtekst, cta)` – relacja 1080×1920.
- `carousels.py` → slajdy 1080×1350: `s_cover`, `s_photo`, `s_list`, `s_cta`.
- `reels.py` → `render(nazwa, sceny)` – rolka MP4 1080×1920, sceny `(kadr, sekundy, overlay(...))`.
- `przyklad_listopad.py` – wzór pełnego miesiąca (relacje, karuzele, rolki).

Wyniki trafiają do `out/` (lub `$GADKA_OUT`), potem kopiujemy je do `RRRR-MM/relacje|karuzele/RRRR-MM-DD|rolki`.
Publiczny adres pliku: `https://raw.githubusercontent.com/Bu3blex/gadka-media/main/<ścieżka>`.

Zasady: relacje bez tekstu w Metricool (tekst jest na grafice), nagłówki krótkie (max 3 linie), bez nieprawdziwych liczb,
bez porównań z nazwaną konkurencją, bez wątków rodzinnych w zespole. Po wygenerowaniu zawsze obejrzyj podgląd.
