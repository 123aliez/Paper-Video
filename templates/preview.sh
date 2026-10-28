#!/bin/bash
# Usage: preview.sh <module> <Scene> [times...]  -> 480p render + contact sheet of frames at the given seconds
# Prints "late by" sync warnings and errors, then the path of the contact sheet (open it with Read).
set -e
cd "$(dirname "$0")"
MOD=$1; SC=$2; shift 2
OUT=${PREVIEW_DIR:-build/preview}
mkdir -p "$OUT"
.venv/bin/manim -ql --progress_bar none --media_dir "$OUT/media/$SC" "$MOD.py" "$SC" 2>&1 | grep -E "late by|Traceback|Error:|Exception|File \"$(pwd)" | head -30 || true
VID="$OUT/media/$SC/videos/$MOD/480p15/$SC.mp4"
[ -f "$VID" ] || { echo "no video"; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VID")
echo "duration $DUR"
[ $# -gt 0 ] || exit 0
mkdir -p "$OUT/frames"; rm -f "$OUT"/frames/${SC}_*.png
i=0
for t in "$@"; do
  ffmpeg -v error -y -ss "$t" -i "$VID" -frames:v 1 "$OUT/frames/${SC}_$(printf %02d $i).png"; i=$((i+1))
done
ffmpeg -v error -y -pattern_type glob -i "$OUT/frames/${SC}_*.png" -filter_complex "tile=2x$(( (i+1)/2 )):padding=6:color=white" "$OUT/frames/sheet_${SC}.png"
echo "$OUT/frames/sheet_${SC}.png"
