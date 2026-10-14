# Silnik rolek (Reels 1080×1920)

Każdy folder to jedna rolka. Obraz robi strona HTML w canvasie lub DOM z funkcją `window.renderAt(t)`. Dźwięk jest syntezowany w numpy, a całość składa się w MP4 przez Playwright i ffmpeg.

## Jak to działa
1. `renderXX.py` ustala oś czasu (stałe w sekundach) i zapisuje ją do `data.js` jako `window.DATA`.
2. Ten sam skrypt składa ścieżkę dźwiękową w numpy (44,1 kHz) i zapisuje `_mix.wav`.
3. Odpala `python3 -m http.server <PORT>` w folderze rolki i Chromium przez Playwright z `--no-proxy-server` (Chromium jest w `/opt/pw-browsers`).
4. Dla każdej klatki wywołuje `renderAt(t)`, robi zrzut JPEG i przekazuje go do ffmpeg (image2pipe, mjpeg, 30 fps, libx264, AAC).
5. Podgląd wybranych klatek bez renderowania całości: `PREV=1.0,3.5,8.2 python3 renderXX.py`, wynik w `prev.jpg`.
6. Wysyłka: przekoduj do około 7 Mb/s, żeby plik miał mniej niż 30 MB.

## Wymagane w folderze rolki
- `img/`: zdjęcia studia (u Gadki 1800×1013) i `noise.png`.
- `fonts/`: kopie Inter Display (`/usr/share/fonts/opentype/inter/`).
- `logo.png` i `logo_black.png`.

Pliki `img/`, `fonts/` i logo nie są w tym folderze, trzeba je skopiować przed renderem.

## Gotowe koncepty (Gadka studio)
| folder | pomysł | stylistyka i dźwięk |
|---|---|---|
| pov_powiadomienia | powiadomienia na ekranie blokady, paragon | ciemny UI telefonu, deep house |
| koszyk | koszyk sprzętu za tysiące zł kontra Gadka 300 zł | kremowy UI sklepu, deep house |
| match | swipe: odrzucamy „szybki zarobek”, match z Gadką | śliwkowo-różowy, lo-fi Rhodes |
| rpg_8bit | gra RPG: ekwipunek, skrzynia, level up | pixel art 270×480 ×4, chiptune |
| zwiastun | zwiastun kinowy, BRAAAM, „WKRÓTCE → JUŻ JUTRO” | kino w pasach, ziarno taśmy |
| pogoda | prognoza pogody dla twórców, mapa mieszkania | grafika TV, funk |
| okup_kolaz | „Mamy Twój podcast”, list z żądaniem okupu | kolaż poklatkowy 12 kl./s, jazz |
| instrukcja | instrukcja montażu podcastu | czarna kreska, ludziki, dzwonki |
| muzeum | muzeum niedokończonych podcastów | galeria, pianino z pogłosem (za długie, za mało dopracowane) |
