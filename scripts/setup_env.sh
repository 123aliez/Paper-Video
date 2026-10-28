#!/bin/bash
# Check / install the toolchain and create the project venv.
# Usage: setup_env.sh <production_dir>
# System: ffmpeg (libx264, libass), poppler-utils, xelatex + xeCJK + ctex fonts, dvisvgm, Noto Sans CJK SC,
#         cairo/pango dev headers (to build manimpango). Python: manim, edge-tts, numpy, pillow, scipy.
set -e
PROD=${1:?usage: setup_env.sh <production_dir>}
mkdir -p "$PROD"
missing=()
for b in ffmpeg ffprobe pdftotext pdftoppm pdfimages pdfinfo xelatex dvisvgm pkg-config; do
  command -v $b >/dev/null || missing+=($b)
done
fc-list | grep -q "Noto Sans CJK SC" || missing+=(fonts-noto-cjk)
pkg-config --exists pangocairo 2>/dev/null || missing+=(pango-dev)
if [ ${#missing[@]} -gt 0 ]; then
  echo "missing: ${missing[*]}"
  if command -v apt-get >/dev/null && sudo -n true 2>/dev/null; then
    echo "installing with apt (several minutes)..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
      ffmpeg poppler-utils texlive-latex-base texlive-latex-recommended texlive-latex-extra \
      texlive-fonts-recommended texlive-science texlive-xetex texlive-lang-chinese dvisvgm \
      fonts-noto-cjk libcairo2-dev libpango1.0-dev pkg-config python3-dev build-essential
  else
    echo "cannot install automatically: ask the user to install the packages above"; exit 1
  fi
fi
ffmpeg -hide_banner -filters 2>/dev/null | grep -q " ass " || { echo "ffmpeg lacks libass (needed to burn subtitles)"; exit 1; }
UV=$(command -v uv || echo ~/.local/bin/uv)
if [ ! -x "$UV" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  UV=~/.local/bin/uv
fi
cd "$PROD"
[ -d .venv ] || "$UV" venv -q --python 3.12 .venv
"$UV" pip install -q --python .venv/bin/python manim edge-tts numpy pillow scipy
.venv/bin/python -c "import manim, edge_tts; print('manim', manim.__version__, '| edge-tts', edge_tts.__version__)"
echo "env ok: $PROD/.venv"
