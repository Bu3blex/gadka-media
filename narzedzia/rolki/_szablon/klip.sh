#!/usr/bin/env bash
# Własne nagranie -> klatki 1080x1920 (30 fps) + dźwięk.
# Użycie: bash klip.sh nagranie.mp4 nazwa [start_s] [długość_s]
set -e
IN="$1"; N="$2"; SS="${3:-0}"; DUR="${4:-}"
mkdir -p "klipy/$N"
ffmpeg -loglevel error -y -ss "$SS" ${DUR:+-t $DUR} -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" -q:v 3 "klipy/$N/%04d.jpg"
ffmpeg -loglevel error -y -ss "$SS" ${DUR:+-t $DUR} -i "$IN" -vn -ac 1 -ar 44100 "klipy/$N.wav" 2>/dev/null || true
echo "klipy/$N: $(ls klipy/$N | wc -l) klatek"
