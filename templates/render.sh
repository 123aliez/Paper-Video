#!/bin/bash
# Render every scene, 4 at a time. Usage: render.sh [Scene ...]  (default: all)
# RES=3840,2160 ./render.sh  renders 4K (then set "quality": "2160p30" in video.json).
# Each scene gets its own media dir: parallel manim processes share no TeX cache, so they never race.
cd "$(dirname "$0")"
export RES=${RES:-1920,1080}
JOBS=${JOBS:-4}
mkdir -p render
list() {
  echo "extras Intro"; echo "extras Outro"
  .venv/bin/python -c "
import json
for s in json.load(open('shots.json')):
    print('ch' + s['id'].split('-')[0], 'S' + s['id'].replace('-', '_'))"
}
if [ $# -gt 0 ]; then
  for sc in "$@"; do list | grep " $sc\$"; done
else
  # longest shots first for better packing
  list | .venv/bin/python -c "
import sys, json
t = {('S'+s['id'].replace('-','_')): json.load(open('timing/'+s['id']+'.json'))['duration'] for s in json.load(open('shots.json'))}
rows = [l.split() for l in sys.stdin]
rows.sort(key=lambda r: -t.get(r[1], 1))
print('\n'.join(' '.join(r) for r in rows))"
fi | xargs -P "$JOBS" -L 1 bash -c '.venv/bin/manim -r "$RES" --fps 30 --disable_caching --progress_bar none --media_dir "render/$1" "$0.py" "$1" > "render/$1.log" 2>&1 && echo "ok $1" || echo "FAIL $1 (see render/$1.log)"'
grep -h "late by" render/*.log 2>/dev/null | sort | uniq || true
