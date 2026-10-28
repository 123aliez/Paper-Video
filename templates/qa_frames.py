"""Sample frames from the final video (2 per shot) into labelled contact sheets for review.

Usage: python qa_frames.py [out_dir]     (default build/qa; open sheet_*.png with Read)
"""
import subprocess
import sys
from pathlib import Path

import assemble

ROOT = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "qa"
OUT.mkdir(parents=True, exist_ok=True)
video = assemble.OUT_DIR / f"{assemble.NAME}.mp4"
t, pts = 0.0, []
for mod, scene, sid in assemble.segments():
    d = assemble.frames(assemble.video_path(mod, scene)) / assemble.FPS
    if sid:
        pts += [(f"{sid}a", t + d * 0.55), (f"{sid}b", t + d - 0.7)]
    t += d
for f in OUT.glob("f_*.png"):
    f.unlink()
for name, ts in pts:
    label = f"{name}  {int(ts // 60)}\\:{ts % 60:05.2f}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", f"scale=960:-1,drawtext=text='{label}':x=8:y=h-th-8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6",
                    str(OUT / f"f_{name}.png")], check=True)
files = sorted(OUT.glob("f_*.png"), key=lambda p: [int(x) if x.isdigit() else x
                                                  for x in p.stem[2:-1].split("-")] + [p.stem[-1]])
for i in range(0, len(files), 6):
    grp = files[i:i + 6]
    args = []
    for f in grp:
        args += ["-i", str(f)]
    n = len(grp)
    layout = "|".join(f"{(k % 2) * 960}_{(k // 2) * 540}" for k in range(n))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex",
                    f"xstack=inputs={n}:layout={layout}:fill=white" if n > 1 else "null",
                    str(OUT / f"sheet_{i // 6:02d}.png")], check=True)
print(OUT)
