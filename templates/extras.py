"""Title card and closing card, filled from video.json."""
from common import *


def fit(mob, w=13.0):
    if mob.width > w:
        mob.scale_to_fit_width(w)
    return mob


class _Card(Scene):
    seg = "intro"
    length = INTRO_LEN

    def setup(self):
        tl = timeline()
        self.g0, self.total = tl[self.seg], tl["total"]

    def bar(self):
        x0, x1 = -config.frame_width / 2, config.frame_width / 2
        y = -config.frame_height / 2 + 0.03
        track = Line([x0, y, 0], [x1, y, 0], stroke_width=4, color=FAINT)
        bar = Line([x0, y, 0], [x0 + 0.001, y, 0], stroke_width=4, color=ACCENT)
        bar.add_updater(lambda m: m.put_start_and_end_on(
            [x0, y, 0], [x0 + max(1e-3, (self.g0 + self.renderer.time) / self.total * (x1 - x0)), y, 0]))
        self.add(track, bar)
        return track, bar


class Intro(_Card):
    seg = "intro"
    length = INTRO_LEN

    def construct(self):
        self.bar()
        kicker = TB(CFG.get("kicker", "论文讲解"), size=26, color=BG)
        kb = RoundedRectangle(corner_radius=0.1, width=kicker.width + 0.4, height=0.52, fill_color=ACCENT,
                              fill_opacity=1, stroke_width=0)
        kick = VGroup(kb, kicker.move_to(kb))
        zh = fit(TB(CFG["title_zh"], size=44))
        en = fit(T(CFG["title_en"], size=30, color=MUTED))
        au = fit(T(CFG["authors"], size=19, color=MUTED))
        ven = fit(T(CFG["venue"], size=24, color=ACCENT))
        VGroup(kick, zh, en, au, ven).arrange(DOWN, buff=0.32).move_to(UP * 0.3)
        line = Line(LEFT * 3, RIGHT * 3, color=ACCENT, stroke_width=2).next_to(en, DOWN, 0.16)
        au.next_to(line, DOWN, 0.2)
        ven.next_to(au, DOWN, 0.3)
        self.play(FadeIn(kick, shift=DOWN * 0.2), FadeIn(zh, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(en), Create(line), run_time=0.6)
        self.play(FadeIn(au), FadeIn(ven), run_time=0.6)
        self.wait(self.length - 2.0 - 0.45)
        self.play(FadeOut(VGroup(kick, zh, en, line, au, ven)), run_time=0.45)


class Outro(_Card):
    seg = "outro"
    length = OUTRO_LEN

    def construct(self):
        self.bar()
        t = TB("感谢观看", size=52)
        lines = [fit(T(s, size=21, color=MUTED)) for s in CFG.get("outro", [])]
        note = CFG.get("outro_note", "文中数字均对照论文 PDF 核实；演示数值为自拟，已在画面标注")
        n = fit(T(note, size=19, color=FAINT))
        g = VGroup(t, *lines, n).arrange(DOWN, buff=0.32).move_to(UP * 0.4)
        self.play(FadeIn(t, shift=UP * 0.2), run_time=0.6)
        self.play(*[FadeIn(m) for m in (*lines, n)], run_time=0.6)
        self.wait(self.length - 1.2 - 0.8)
        self.play(FadeOut(g), run_time=0.8)
