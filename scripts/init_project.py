"""Create a production folder from the skill templates.

Usage: python init_project.py <work_dir>
  copies templates/* into <work_dir>/production/ (never overwrites an existing file) and
  creates the asset/output folders. Fill production/video.json afterwards.
"""
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
work = Path(sys.argv[1]).resolve()
prod = work / "production"
for d in ("assets/pages", "assets/figs", "assets/text", "assets/crops", "audio", "timing", "render", "build"):
    (prod / d).mkdir(parents=True, exist_ok=True)
for f in sorted((SKILL / "templates").iterdir()):
    dst = prod / f.name
    if dst.exists():
        print("keep", dst.name)
        continue
    shutil.copy2(f, dst)
    print("copy", dst.name)
print(prod)
