"""Shared look, timing and paper-crop helpers for every shot.

Every chapter module does `from common import *` and defines one `Shot` subclass per shot:

    class S2_3(Shot):          # shot id "2-3"
        sid = "2-3"
        def body(self):
            eq = M(r"E[w\\ell]=E[w]E[\\ell]+\\mathrm{Cov}(w,\\ell)", size=44)
            self.play_at(self.cue("恒等式"), Write(eq), run_time=1.0)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from manim import *

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
CFG = json.loads((ROOT / "video.json").read_text())

config.background_color = "#0E1117"

# ---------------------------------------------------------------- palette
# Pick colours by role, and keep the role fixed for the whole video.
BG = "#0E1117"
PANEL = "#1A1F2B"
INK = "#ECEFF4"
MUTED = "#8A93A6"
FAINT = "#3A4253"
ACCENT = "#F5C542"     # the paper's method / the thing the viewer should look at
BASELINE = "#5B8DEF"   # the baseline or "old way" it is compared with
WARN = "#FF6B6B"       # caveats, "论文未说明", demo values
GOOD = "#5CC98B"       # correct outcomes, passes
ORANGE = "#F28C38"     # secondary emphasis
PINK = "#F49AA0"
TEAL = "#4FD1C5"
PURPLE = "#B794F4"

FONT = "Noto Sans CJK SC"

CJK = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
CJK.add_to_preamble(
    r"\usepackage{xeCJK}\setCJKmainfont{Noto Sans CJK SC}"
    r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{mathrsfs}"
)
MathTex.set_default(tex_template=CJK)
Tex.set_default(tex_template=CJK)


def T(s, size=30, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def TB(s, size=30, color=INK, **kw):
    return T(s, size=size, color=color, weight=BOLD, **kw)


def M(*tex, size=40, color=INK, **kw):
    return MathTex(*tex, font_size=size, color=color, **kw)


def tag(text, color=WARN, size=22, fill_opacity=0.14):
    """Small rounded label, e.g. a caveat or a source note. `\\n` splits lines."""
    if "\n" in text:
        t = VGroup(*[T(l, size=size, color=color) for l in text.split("\n")]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    else:
        t = T(text, size=size, color=color)
    box = RoundedRectangle(
        corner_radius=0.12, width=t.width + 0.36, height=t.height + 0.22,
        stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity,
    )
    return VGroup(box, t.move_to(box))


def card(mob, pad=0.3, color=PANEL, stroke=FAINT, radius=0.18):
    box = RoundedRectangle(
        corner_radius=radius, width=mob.width + 2 * pad, height=mob.height + 2 * pad,
        fill_color=color, fill_opacity=1, stroke_color=stroke, stroke_width=1.5,
    ).move_to(mob)
    return VGroup(box, mob)


def hl_box(mob, color=ACCENT, buff=0.08, fill=0.12, width=3):
    return SurroundingRectangle(
        mob, color=color, buff=buff, stroke_width=width, fill_color=color, fill_opacity=fill,
        corner_radius=0.06,
    )


# ---------------------------------------------------------------- timing
SHOTS = json.loads((ROOT / "shots.json").read_text())
SHOT_BY_ID = {s["id"]: s for s in SHOTS}
LEAD = 0.25      # silence before the narration of each shot (assemble.LEAD must match)
TAIL = 0.55      # silence after it (shot gap)
INTRO_LEN = 4.0
OUTRO_LEN = 4.0


def timing(sid):
    return json.loads((ROOT / "timing" / f"{sid}.json").read_text())


def shot_len(sid):
    return LEAD + timing(sid)["duration"] + TAIL + SHOT_BY_ID[sid].get("tail", 0.0)


def timeline():
    """Global start time of every segment: intro, shots..., outro."""
    t, out = INTRO_LEN, {"intro": 0.0}
    for s in SHOTS:
        out[s["id"]] = t
        t += shot_len(s["id"])
    out["outro"] = t
    out["total"] = t + OUTRO_LEN
    return out


def chapter_of(sid):
    return sid.split("-")[0]


def _chapters():
    """{"1": ("第一章", "开场与痛点"), ...} from the `chapter` field of shots.json."""
    out = {}
    for s in SHOTS:
        ch = chapter_of(s["id"])
        if ch not in out:
            m = re.match(r"(第\S+章)\s*(.*)", s["chapter"])
            out[ch] = (m.group(1), m.group(2)) if m else (f"第{ch}章", s["chapter"])
    return out


CHAPTERS = _chapters()


def chapter_tag(ch):
    n = TB(f"{int(ch):02d}", size=20, color=BG)
    nb = RoundedRectangle(corner_radius=0.08, width=0.52, height=0.34, fill_color=ACCENT,
                          fill_opacity=1, stroke_width=0)
    n.move_to(nb)
    t = T(CHAPTERS[ch][1], size=20, color=MUTED)
    g = VGroup(VGroup(nb, n), t).arrange(RIGHT, buff=0.18)
    return g.to_corner(UL, buff=0.32)


class Shot(Scene):
    """One narrated shot. Subclasses implement `body()` and use `cue()` / `play_at()` for sync.

    The scene clock starts at 0 when the shot starts; narration starts at LEAD. `construct()`
    pads the scene to exactly `shot_len(sid)` seconds so audio and video stay aligned.
    """

    sid = "0-0"
    carry_out = False   # True: leave the last frame on screen (next shot continues it)
    carry_in = False    # True: no chapter intro / fade-in (continues previous shot)
    skip_intro = False  # True: body brings in the corner tag itself (use on shot 1-1)

    # ---- timing
    def setup(self):
        self.tm = timing(self.sid)
        self.text = self.tm["tts"]
        self.words = self.tm["words"]
        self.length = shot_len(self.sid)
        tl = timeline()
        self.g0, self.total = tl[self.sid], tl["total"]
        self.chapter = chapter_of(self.sid)
        self.persist = []

    def cue(self, phrase, k=0, end=False, offset=0.0):
        """Time (s, scene clock) at which `phrase` (k-th occurrence, 0-based) starts (or ends) being
        spoken. `phrase` is matched against the TTS text, i.e. after video.json tts_replace."""
        pos = -1
        for _ in range(k + 1):
            pos = self.text.find(phrase, pos + 1)
            if pos < 0:
                raise ValueError(f"[{self.sid}] cue not found: {phrase!r} (k={k})")
        c = pos + len(phrase) if end else pos
        t = self.words[-1]["t1"]
        for w in self.words:
            if w["c1"] > c:
                if w["c0"] >= c:
                    t = w["t0"]
                else:
                    f = (c - w["c0"]) / max(1, w["c1"] - w["c0"])
                    t = w["t0"] + f * (w["t1"] - w["t0"])
                break
        return LEAD + t + offset

    def now(self):
        return self.renderer.time

    def at(self, t):
        dt = t - self.now()
        if dt > 1e-3:
            self.wait(dt)
        elif dt < -0.25:
            print(f"[{self.sid}] late by {-dt:.2f}s at t={t:.2f}", file=sys.stderr)

    def play_at(self, t, *anims, **kw):
        self.at(t)
        self.play(*anims, **kw)

    def end_of_speech(self):
        return LEAD + self.tm["duration"]

    # ---- chrome
    def add_chrome(self):
        x0, x1 = -config.frame_width / 2, config.frame_width / 2
        y = -config.frame_height / 2 + 0.03
        track = Line([x0, y, 0], [x1, y, 0], stroke_width=4, color=FAINT)
        bar = Line([x0, y, 0], [x0 + 0.001, y, 0], stroke_width=4, color=ACCENT)

        def upd(m):
            frac = (self.g0 + self.now()) / self.total
            m.put_start_and_end_on([x0, y, 0], [x0 + max(1e-3, frac * (x1 - x0)), y, 0])

        bar.add_updater(upd)
        self.add(track, bar)
        self.tagm = chapter_tag(self.chapter)
        idx = [s["id"] for s in SHOTS].index(self.sid)
        is_first = idx == 0 or chapter_of(SHOTS[idx - 1]["id"]) != self.chapter
        self.is_chapter_start = is_first and not self.carry_in
        if not self.is_chapter_start:
            self.add(self.tagm)
        self.persist = [track, bar, self.tagm]

    def chapter_intro(self, hold=0.9):
        """Big chapter title that shrinks into the corner tag. Takes ~hold+1.2 s."""
        head, title = CHAPTERS[self.chapter]
        big = VGroup(TB(head, size=34, color=ACCENT), TB(title, size=56)).arrange(DOWN, buff=0.3)
        if big.width > 12.5:
            big.scale_to_fit_width(12.5)
        line = Line(LEFT * 2.2, RIGHT * 2.2, color=ACCENT, stroke_width=3).next_to(big, DOWN, 0.35)
        self.play(FadeIn(big, shift=UP * 0.2), Create(line), run_time=0.6)
        self.wait(hold)
        self.play(ReplacementTransform(VGroup(big, line), self.tagm), run_time=0.6)

    def source(self, text):
        """Corner note with the paper location of what is on screen, e.g. "出处：Table 1"."""
        t = T(text, size=18, color=MUTED)
        return t.to_corner(UR, buff=0.36)

    def clear_stage(self, run_time=0.35, keep=()):
        keep = set(map(id, list(self.persist) + list(keep)))
        mobs = [m for m in self.mobjects if id(m) not in keep]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def construct(self):
        self.add_chrome()
        if self.is_chapter_start and not self.skip_intro:
            self.chapter_intro()
        self.body()
        end = self.length
        if self.carry_out:
            self.at(end)
        else:
            self.at(end - 0.4)
            self.clear_stage(run_time=0.35)
            self.at(end)
        # pad to the exact frame count
        rem = end - self.now()
        if rem > 1e-3:
            self.wait(rem)

    def body(self):
        raise NotImplementedError


# ---------------------------------------------------------------- paper crops
PAGE_DPI = 400
_WORDS = None


def words():
    """Per-page word boxes (pt) written by pdf_assets.py: [[{t, x0, y0, x1, y1}, ...], ...]."""
    global _WORDS
    if _WORDS is None:
        _WORDS = json.loads((ASSETS / "words.json").read_text())
    return _WORDS


def find_word(page, text, x=None, y=None, region=None):
    """Bounding box (pt) of a word on a page; nearest to (x, y) or inside region (x0,y0,x1,y1)."""
    cands = [w for w in words()[page - 1] if w["t"] == text]
    if region:
        x0, y0, x1, y1 = region
        cands = [w for w in cands if x0 <= (w["x0"] + w["x1"]) / 2 <= x1 and y0 <= (w["y0"] + w["y1"]) / 2 <= y1]
    if not cands:
        raise ValueError(f"word {text!r} not found on page {page} in {region}")
    if x is not None and y is not None:
        cands.sort(key=lambda w: ((w["x0"] + w["x1"]) / 2 - x) ** 2 + ((w["y0"] + w["y1"]) / 2 - y) ** 2)
    w = cands[0]
    return (w["x0"], w["y0"], w["x1"], w["y1"])


def union_box(*boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


class Crop(Group):
    """A raster crop of a page (pt box) or of a figure image (px box), on a white card.

    src: page number (int, uses assets/pages/p{n}.png at PAGE_DPI) or an image path under assets/.
    `pt(x, y)` converts source coordinates (pt for pages, px for images) to scene points,
    following the crop wherever it has been moved or scaled.
    """

    def __init__(self, src, box, height=None, width=None, scale_px=1.6, pad=0.12, radius=0.1,
                 card_color=WHITE, **kw):
        super().__init__(**kw)
        if isinstance(src, int):
            path = ASSETS / "pages" / f"p{src}.png"
            k = PAGE_DPI / 72.0
        else:
            path = ASSETS / src
            k = 1.0
        x0, y0, x1, y1 = box
        self.box, self.k = box, k
        im = Image.open(path).convert("RGB").crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
        aspect = im.width / im.height
        if height is None:
            height = width / aspect
        w_units = height * aspect
        # keep ~scale_px source pixels per output pixel at 1080p, never upsample
        target_w = int(min(im.width, w_units * config.pixel_width / config.frame_width * scale_px))
        if target_w < im.width:
            im = im.resize((target_w, int(target_w / aspect)), Image.LANCZOS)
        key = hashlib.md5(f"{path}|{box}|{im.size}".encode()).hexdigest()[:12]
        (ASSETS / "crops").mkdir(exist_ok=True)
        out = ASSETS / "crops" / f"{key}.png"
        if not out.exists():
            im.save(out)
        self.img = ImageMobject(str(out)).set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])
        self.img.height = height
        self.bg = RoundedRectangle(
            corner_radius=radius, width=self.img.width + 2 * pad, height=self.img.height + 2 * pad,
            fill_color=card_color, fill_opacity=1, stroke_width=0,
        )
        self.add(self.bg, self.img)

    def pt(self, x, y):
        x0, y0, x1, y1 = self.box
        ul = self.img.get_corner(UL)
        fx = (x - x0) / (x1 - x0)
        fy = (y - y0) / (y1 - y0)
        return ul + RIGHT * fx * self.img.width + DOWN * fy * self.img.height

    def rect(self, bx, color=ACCENT, pad=1.2, fill=0.18, width=3, radius=0.04):
        """Highlight rectangle over a source box (x0,y0,x1,y1)."""
        x0, y0, x1, y1 = bx
        a = self.pt(x0 - pad, y0 - pad)
        b = self.pt(x1 + pad, y1 + pad)
        r = RoundedRectangle(
            corner_radius=radius, width=abs(b[0] - a[0]), height=abs(b[1] - a[1]),
            stroke_color=color, stroke_width=width, fill_color=color, fill_opacity=fill,
        )
        return r.move_to((a + b) / 2)

    def veil(self, keep_boxes=(), opacity=0.6, color=BLACK):
        """A dark veil over the crop with holes over keep_boxes (source coords)."""
        veil = Rectangle(width=self.img.width, height=self.img.height).move_to(self.img)
        holes = [self.rect(b, pad=1.5) for b in keep_boxes]
        if holes:
            veil = Difference(veil, Union(*holes) if len(holes) > 1 else holes[0])
        veil.set_fill(color, opacity).set_stroke(width=0)
        return veil
