# Silnik animowanych rolek (Reels/TikTok 1080×1920)

Obraz powstaje w przeglądarce: canvas z funkcją `window.renderAt(t)`. Dźwięk jest syntezowany w numpy. Całość składa się w MP4 przez Playwright i ffmpeg.

## Szybki start
```bash
bash narzedzia/rolki/_szablon/przygotuj.sh /ścieżka/do/nowej_rolki   # szablon + fonty + logo + zdjęcia + szum
cd /ścieżka/do/nowej_rolki
bash klip.sh nagranie.mp4 klipA 3.5 4        # (opcjonalnie) własne nagranie -> klatki 1080x1920 + wav
SAFE=1 PREV=1,4,9 python3 render.py          # podgląd klatek z ramką strefy bezpiecznej -> prev.jpg
COVER=1 python3 render.py                    # okładka -> okladka.jpg
python3 render.py                            # pełny render -> rolka.mp4 i rolka_ig.mp4 (<30 MB)
```

## Zasady
- **Strefa bezpieczna rolki:** x 120–960, y 280–1580. Poza nią mogą być tylko tło i dekoracje.
- **Okładka:** wszystko w kwadracie y 420–1500, x 100–980.
- **Długość:** 20–25 s. Hak w pierwszej sekundzie. Sceny wchodzą na uderzenia muzyki.
- **Zawsze** oglądaj podgląd przed pełnym renderem.
- Poziome zdjęcia (1800×1013) przycięte na cały pionowy ekran tracą treść i źle się kadrują (uwaga klienta przy `capcut`). Pełny ekran tylko z pionowych ujęć/nagrań, poziome zdjęcia w ramkach, kartach i oknach.

## Gotowe koncepty (Gadka studio)
| folder | pomysł | stylistyka i dźwięk |
|---|---|---|
| pov_powiadomienia | powiadomienia na ekranie blokady, paragon | ciemny UI telefonu, deep house |
| koszyk | koszyk sprzętu za tysiące zł kontra Gadka 300 zł | kremowy UI sklepu, deep house |
| match | swipe: „szybki zarobek” w lewo, match z Gadką | śliwkowo-różowy, lo-fi Rhodes |
| rpg_8bit | gra RPG: ekwipunek, skrzynia, level up | pixel art, chiptune |
| zwiastun | zwiastun kinowy, „WKRÓTCE → JUŻ JUTRO” | kino w pasach, BRAAAM |
| pogoda | prognoza pogody dla twórców | grafika TV, funk |
| okup_kolaz | „Mamy Twój podcast”, list z żądaniem okupu | kolaż poklatkowy, jazz |
| instrukcja | instrukcja montażu podcastu | czarna kreska, dzwonki |
| muzeum | muzeum niedokończonych podcastów | galeria (za długie, za mało dopracowane) |
| podsumowanie | podsumowanie roku jako podcaster | kolorowe karty, electro-pop |
| tarot | 3 karty: przeszłość, teraźniejszość, przyszłość | granat i złoto, harfa, ciepły finał |
| noc | „Ty o 2:37 w nocy”: zapytania w wyszukiwarce, wynik Gadka studio | ciemny UI, nocny synthwave, stukot klawiatury |
| przepis | „Przepis na podcast”: składniki do garnka, kroki, „nie w kuchni!” | kremowy papier, Lora italic, bossa nova |
| flagi | „Red flags vs green flags” (18–30) | neo-brutalizm – oceniony jako „lipny, niemłodzieżowy”, nie powtarzać |
| capcut | „ziomek nagrywa podcast w łazience 💀” (18–30) | styl TikTok/CapCut: napisy słowo po słowie, punch zoomy, drill z dropem |
| okladki | skrypty okładek: typografia (`final_a.py`) i okładki z silnika (`cover_snap.py`) | |

Zdjęcia studia są w `zrodla/` (numery P1160xxx → `img/xxx.jpg`), a logo z przezroczystym tłem w `marka/`.
