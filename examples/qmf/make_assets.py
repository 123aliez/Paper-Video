"""Procedural illustrations: a stylised bedroom photo, its depth map, and noisy copies."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets"
W, H = 800, 600

# Room geometry (pixel polygons, painted back to front).
BACK = [(210, 130), (590, 130), (590, 380), (210, 380)]
FLOOR = [(0, 600), (800, 600), (590, 380), (210, 380)]
LEFT = [(0, 0), (210, 130), (210, 380), (0, 600)]
RIGHT = [(800, 0), (590, 130), (590, 380), (800, 600)]
CEIL = [(0, 0), (800, 0), (590, 130), (210, 130)]
WINDOW = [(400, 175), (545, 175), (545, 300), (400, 300)]
HEAD = [(255, 255), (470, 255), (470, 380), (255, 380)]
MATTRESS = [(245, 360), (480, 360), (585, 505), (150, 505)]
FRONT = [(150, 505), (585, 505), (585, 548), (150, 548)]
BLANKET = [(200, 425), (532, 425), (585, 505), (150, 505)]
BLANKET_F = [(150, 505), (585, 505), (585, 540), (150, 540)]
PILLOW = (285, 335, 445, 382)
STAND = [(120, 390), (195, 390), (195, 470), (120, 470)]
LAMP = [(140, 330), (178, 330), (188, 365), (130, 365)]
LAMP_POLE = [(156, 365), (162, 365), (162, 390), (156, 390)]


def mask(poly=None, ellipse=None):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    if poly:
        d.polygon(poly, fill=255)
    if ellipse:
        d.ellipse(ellipse, fill=255)
    return np.asarray(m) > 0


def rgb_image():
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    img = np.zeros((H, W, 3))

    def paint(m, color, shade=None):
        c = np.array(color, float) / 255.0
        val = c[None, None, :] * (shade[..., None] if shade is not None else 1.0)
        img[m] = val[m] if shade is not None else c

    paint(mask(CEIL), (238, 233, 224), 0.95 + 0.05 * ys / 130)
    paint(mask(LEFT), (214, 196, 170), 0.82 + 0.15 * xs / 210)
    paint(mask(RIGHT), (222, 205, 180), 0.92 - 0.1 * (xs - 590) / 210)
    paint(mask(BACK), (232, 219, 198))
    floor_shade = 0.75 + 0.25 * (ys - 380) / 220
    planks = 0.94 + 0.06 * (np.sin((xs - 400) / np.maximum(ys - 300, 1) * 60) > 0.92)
    paint(mask(FLOOR), (170, 118, 74), floor_shade * planks)
    paint(mask(WINDOW), (150, 200, 240), 0.9 + 0.15 * (ys - 175) / 125)
    paint(mask(STAND), (120, 82, 52))
    paint(mask(LAMP_POLE), (90, 90, 90))
    paint(mask(LAMP), (250, 226, 160))
    paint(mask(HEAD), (110, 74, 46))
    paint(mask(MATTRESS), (240, 240, 236))
    paint(mask(FRONT), (210, 210, 205))
    paint(mask(BLANKET), (72, 118, 186), 0.85 + 0.2 * (ys - 425) / 80)
    paint(mask(BLANKET_F), (58, 98, 160))
    paint(mask(ellipse=PILLOW), (250, 250, 248))
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([400, 175, 545, 300], outline=(250, 250, 250), width=8)
    d.line([(472, 175), (472, 300)], fill=(250, 250, 250), width=6)
    d.line([(400, 237), (545, 237)], fill=(250, 250, 250), width=6)
    return im.filter(ImageFilter.SMOOTH)


def depth_image():
    """Near = bright, far = dark."""
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    dep = np.zeros((H, W))
    far, near = 0.12, 0.95

    def paint(m, v):
        dep[m] = v[m] if isinstance(v, np.ndarray) else v

    paint(mask(CEIL), far + (near - far) * (1 - ys / 130) * 0.9)
    paint(mask(LEFT), far + (near - far) * (1 - xs / 210))
    paint(mask(RIGHT), far + (near - far) * ((xs - 590) / 210))
    paint(mask(BACK), far)
    paint(mask(FLOOR), far + (near - far) * (ys - 380) / 220)
    paint(mask(WINDOW), far)
    paint(mask(STAND), 0.45)
    paint(mask(LAMP_POLE), 0.42)
    paint(mask(LAMP), 0.42)
    paint(mask(HEAD), 0.22)
    paint(mask(MATTRESS), 0.3 + 0.45 * (ys - 360) / 145)
    paint(mask(BLANKET), 0.3 + 0.45 * (ys - 360) / 145)
    paint(mask(FRONT), 0.8)
    paint(mask(BLANKET_F), 0.8)
    paint(mask(ellipse=PILLOW), 0.28)
    g = (np.clip(dep, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(g).convert("RGB").filter(ImageFilter.SMOOTH)


def noisy(im, eps, seed=0):
    """Add N(0, eps) noise in ImageNet-normalised units (std 0.225 per unit)."""
    rng = np.random.default_rng(seed)
    a = np.asarray(im).astype(float) / 255.0
    n = rng.normal(0.0, np.sqrt(eps) * 0.225, a.shape) if eps > 0 else 0
    return Image.fromarray((np.clip(a + n, 0, 1) * 255).astype(np.uint8))


if __name__ == "__main__":
    rgb = rgb_image()
    rgb.save(OUT / "room_rgb.png")
    depth_image().save(OUT / "room_depth.png")
    small = rgb.resize((400, 300), Image.LANCZOS)
    for eps in (0, 5, 10):
        noisy(small, eps, seed=eps).save(OUT / f"room_noise_{eps}.png")
    print("ok")
