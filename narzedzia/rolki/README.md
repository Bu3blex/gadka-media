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
| jedno_studio | „Jedno studio. Wiele możliwości.” z prawdziwych nagrań: hook z trzech szerokich planów, po jednym ujęciu z aranżacji, sprzęt, cena | minimalizm z klasą: mało tekstu, kapitaliki + pomarańczowa kreska, miękkie przejścia, elegancki deep house |
| plansze_nagrania | „Jeden podcast. Wiele scenografii.”: kremowa plansza ↔ nagranie w pełnym kadrze, sprzęt jak karta produktu, cena | jasny, magazynowy, nu-disco |
| okladki | skrypty okładek: typografia (`final_a.py`) i okładki z silnika (`cover_snap.py`) | |

Zdjęcia studia są w `zrodla/` (numery P1160xxx → `img/xxx.jpg`), a logo z przezroczystym tłem w `marka/`.

## Nadchodzące materiały (od klienta)
Klient dośle wiele nagrań osób siedzących w Gadka studio i rozmawiających ze sobą (prowadzą podcast), nagranych przy różnych ścianach i aranżacjach. Cel: pokazać wszystko, co wyróżnia studio (różne klimaty wnętrza, sprzęt, komfort rozmowy).
Pomysły do wykorzystania:
- „Jedna rozmowa, wiele klimatów”: ta sama rozmowa leci dalej, a przy każdym cięciu zmienia się ściana/scenografia (cięcia na gest lub słowo).
- „Wybierz swój klimat”: przewijanie aranżacji jak wybór motywu/filtra, z nazwą klimatu na naklejce.
- Najlepsze momenty i śmieszne wpadki z rozmów + napisy słowo po słowie (CapCut) z prawdziwym głosem.
- Hak z najmocniejszego zdania z rozmowy, potem korzyści i cena.
Nie podawać liczby aranżacji (zasada klienta). Nagrania pionowe na pełen ekran, poziome w ramkach.

Otrzymane nagrania (2026-10-28, pionowe 1080×1920, 24 kl./s, cichy dźwięk w tle): BIALA_KOSTKA, CIEMNA_ZASLONA, LAMELE, STOL_RADIOWY (Marcysia/Wiktor, ujęcia 1–2), LAMELE_WIKTOR_KADR_JEDNOOSOBOWY (z kamerą w kadrze), UJECIE_NA_SZEROKI_KADR_1 (trzy szerokie plany jeden nad drugim) i _2/_3 (zbliżenie + szeroki plan). Przy nagraniach klient chce: NIE przycinać kadrów nagrań (żadnych okien/ramek wycinających wideo), montować naprzemiennie nagranie w pełnym kadrze ↔ plansza z tekstem; hook z ceną: kadry pojawiają się błyskawicznie, „2 godziny / 300 zł” wybucha (POW) na środku + hasło „Wynajmij studio podcastowe”; logo wysoko na środku (y≈165, nad głowami ludzi w nagraniach); napisy na ujęciach DUŻE i mówiące co to i dlaczego (nie tylko „clean aesthetic”); w rolkach wystarczy „300 zł” (bez „brutto” – to jest na stronie), zamiast tego „27 m² · sprzęt w cenie”; rolka musi jasno mówić, o co chodzi (wynajem studia podcastowego); używać tylko pasujących ujęć, klimat promocyjny, nowocześnie, z klasą i gustem, bez nadmiaru tekstu i pstrokatych efektów, zawsze z logo i kolorami marki.
