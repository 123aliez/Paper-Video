"""Paper assets for shots: word boxes, page renders, embedded figures, per-page text.

Usage:
  python pdf_assets.py extract <paper.pdf> [--dpi 400]
      assets/words.json        word boxes in pt, per page: [[{t, x0, y0, x1, y1}, ...], ...]
      assets/pages/p{n}.png    every page at --dpi (common.PAGE_DPI must match, default 400)
      assets/figs/img-*.png    embedded raster figures at native resolution (pdfimages)
      assets/text/p{n}.txt     pdftotext -layout per page, for checking numbers against the paper
  python pdf_assets.py find <page> <regex> [--near X Y]
      print words on a page matching regex with their pt boxes (to choose crop / highlight boxes)
  python pdf_assets.py box <page> <x0> <y0> <x1> <y1> [out.png]
      save a quick crop of a page box (pt) to look at before using it in a shot
"""
import json
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def page_count(pdf):
    out = subprocess.check_output(["pdfinfo", str(pdf)]).decode(errors="replace")
    return int(re.search(r"^Pages:\s+(\d+)", out, re.M).group(1))


def extract(pdf, dpi=400):
    pdf = Path(pdf).resolve()
    for d in ("pages", "figs", "text", "crops"):
        (ASSETS / d).mkdir(parents=True, exist_ok=True)
    n = page_count(pdf)
    bbox = ASSETS / "bbox.html"
    subprocess.run(["pdftotext", "-bbox", str(pdf), str(bbox)], check=True)
    html = bbox.read_text(encoding="utf-8")
    pages = []
    for pg in re.findall(r"<page[^>]*>(.*?)</page>", html, re.S):
        pages.append([dict(x0=float(a), y0=float(b), x1=float(c), y1=float(d), t=unescape(w))
                      for a, b, c, d, w in re.findall(
                          r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pg)])
    (ASSETS / "words.json").write_text(json.dumps(pages, ensure_ascii=False))
    for p in range(1, n + 1):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(p), "-l", str(p), "-singlefile",
                        str(pdf), str(ASSETS / "pages" / f"p{p}")], check=True)
        subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), str(pdf),
                        str(ASSETS / "text" / f"p{p}.txt")], check=True)
    subprocess.run(["pdfimages", "-png", "-p", str(pdf), str(ASSETS / "figs" / "img")], check=True)
    figs = sorted((ASSETS / "figs").glob("img-*.png"))
    print(f"{n} pages, {sum(len(p) for p in pages)} words, {len(figs)} embedded images")
    lst = subprocess.check_output(["pdfimages", "-list", str(pdf)]).decode(errors="replace")
    print(lst)


def find(page, pattern, near=None):
    ws = json.loads((ASSETS / "words.json").read_text())[page - 1]
    rx = re.compile(pattern)
    hits = [w for w in ws if rx.search(w["t"])]
    if near:
        x, y = near
        hits.sort(key=lambda w: ((w["x0"] + w["x1"]) / 2 - x) ** 2 + ((w["y0"] + w["y1"]) / 2 - y) ** 2)
    for w in hits:
        print(f'{w["t"]:20s} {w["x0"]:7.2f} {w["y0"]:7.2f} {w["x1"]:7.2f} {w["y1"]:7.2f}')


def box(page, x0, y0, x1, y1, out=None, dpi=400):
    from PIL import Image
    k = dpi / 72.0
    im = Image.open(ASSETS / "pages" / f"p{page}.png")
    im = im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
    out = Path(out) if out else ROOT / "build" / f"box_p{page}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "extract":
        dpi = int(a[a.index("--dpi") + 1]) if "--dpi" in a else 400
        extract(a[1], dpi)
    elif a[0] == "find":
        near = (float(a[a.index("--near") + 1]), float(a[a.index("--near") + 2])) if "--near" in a else None
        find(int(a[1]), a[2], near)
    elif a[0] == "box":
        box(int(a[1]), *map(float, a[2:6]), *(a[6:7]))
    else:
        sys.exit(__doc__)
