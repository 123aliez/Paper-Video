from common import *

# Figure 2 (right half) geometry, in source pixels
F2_BOX = (3700, 0, 7375, 2319)
ELL_C, ELL_A, ELL_B, ELL_ANG = (6105, 1118), 1266, 809, 19 * DEGREES
STATIC_C, STATIC_R = (5392, 1336), 381
OURS_C, OURS_R = (6680, 813), 426
FSTAR = (6710, 782)
P_OURS = (6506, 577)
P_DYN = (6245, 1392)
REG_LABEL = (4380, 430, 5000, 610)


def fig2_right():
    fig = Crop("fig2_clean.png", F2_BOX, height=5.2, scale_px=2.0, pad=0.12)
    fig.move_to([-2.85, 0.35, 0])
    return fig


def px_len(fig, n):
    return n / (F2_BOX[2] - F2_BOX[0]) * fig.img.width


class S3_1(Shot):
    sid = "3-1"
    carry_out = True

    def body(self):
        fig = fig2_right()
        src = self.source("出处：Figure 2（右）及图注")
        self.play_at(self.cue("Figure"), FadeIn(fig, shift=UP * 0.15), FadeIn(src), run_time=0.7)

        items = VGroup()

        def item(sw, text, sub=None, col=INK):
            row = VGroup(sw, T(text, size=22, color=col)).arrange(RIGHT, buff=0.18)
            if sub:
                g = VGroup(row, T(sub, size=18, color=MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
                g[1].shift(RIGHT * 0.4)
                return g
            return row

        x_items = 1.75

        ell = Ellipse(width=2 * px_len(fig, ELL_A), height=2 * px_len(fig, ELL_B), color=WHITE, stroke_width=5)
        ell.rotate(ELL_ANG).move_to(fig.pt(*ELL_C))
        i1 = item(Square(0.26, fill_color="#E6E6E6", fill_opacity=1, stroke_width=0), "灰色区域 = 假设空间",
                  "动态融合能表示的所有模型（候选清单）")
        i1.move_to([x_items, 2.3, 0], aligned_edge=LEFT)
        self.play_at(self.cue("灰色"), Create(ell), run_time=0.8)
        self.play(FadeIn(i1, shift=LEFT * 0.15), ell.animate.set_stroke(opacity=0.0), run_time=0.6)
        self.play_at(self.cue("假设空间"), Indicate(i1[0][1], color=ACCENT, scale_factor=1.06), run_time=0.6)

        blue = Circle(radius=px_len(fig, STATIC_R) + 0.04, color=BASELINE, stroke_width=6).move_to(fig.pt(*STATIC_C))
        i2 = item(Dot(radius=0.13, color=BASELINE), "蓝圈 f_Static：常数权重", "常数权重是动态权重的特例", col=BASELINE)
        i2.next_to(i1, DOWN, 0.4, aligned_edge=LEFT)
        self.play_at(self.cue("静态"), Create(blue), FadeIn(i2[0], shift=LEFT * 0.15), run_time=0.7)
        self.play_at(self.cue("特例"), FadeIn(i2[1]), run_time=0.4)
        quote = T("图注原文：“where the latter is a subset of the former”", size=19, color=MUTED, slant=ITALIC)
        quote.next_to(fig, DOWN, 0.18)
        self.play(FadeIn(quote), run_time=0.4)
        self.play_at(self.cue("蓝"), Indicate(blue, color=BASELINE, scale_factor=1.08), run_time=0.7)
        dyn = Circle(radius=0.14, color=GOOD, stroke_width=5).move_to(fig.pt(*P_DYN))
        i3 = item(Dot(radius=0.13, color=GOOD), "f_Dynamic：一个动态模型", "也在灰色区域里", col=GOOD)
        i3.next_to(i2, DOWN, 0.35, aligned_edge=LEFT)
        self.play_at(self.cue("灰色区域", k=1), Create(dyn), FadeIn(i3, shift=LEFT * 0.15), run_time=0.6)

        yel = Circle(radius=px_len(fig, OURS_R) + 0.04, color=ACCENT, stroke_width=6).move_to(fig.pt(*OURS_C))
        i4 = item(Dot(radius=0.13, color=ACCENT), "黄圈 f_Ours", "加了正则约束的动态融合", col=ACCENT)
        i4.next_to(i3, DOWN, 0.35, aligned_edge=LEFT)
        self.play_at(self.cue("黄圈"), Create(yel), FadeIn(i4, shift=LEFT * 0.15), run_time=0.7)
        reg = fig.rect(REG_LABEL, color=ORANGE, fill=0.12, width=4, pad=25)
        self.play_at(self.cue("正则化"), Create(reg), run_time=0.5)
        warn = tag("图上只标了 “Regularization”，\n没明说它就是满足式 5、式 6 的部分", color=WARN, size=19)
        warn.next_to(i4, DOWN, 0.35, aligned_edge=LEFT)
        self.play_at(self.cue("没"), FadeIn(warn, shift=UP * 0.1), run_time=0.5)

        # leave only the figure for the next shot
        self.at(self.length - 0.45)
        self.play(*[FadeOut(m) for m in (ell, blue, dyn, yel, reg, i1, i2, i3, i4, warn, quote, src)], run_time=0.4)


class S3_2(Shot):
    sid = "3-2"
    carry_in = True

    def body(self):
        fig = fig2_right()
        self.add(fig)
        src = self.source("出处：Figure 2（右）及图注")
        fs = fig.pt(*FSTAR)
        veil = Difference(Rectangle(width=fig.img.width, height=fig.img.height).move_to(fig.img),
                          Circle(radius=0.62).move_to(fs)).set_fill(BLACK, 0.55).set_stroke(width=0)
        ring = Circle(radius=0.62, color=WARN, stroke_width=5).move_to(fs)
        self.play_at(self.cue("叉号"), FadeIn(veil), Create(ring), FadeIn(src), run_time=0.7)

        lines = VGroup(
            T("f* = 真实映射", size=30, color=WARN, weight=BOLD),
            T("理论上最好的预测器", size=22),
            T("只存在于定义里，代码算不出来", size=22),
            M(r"\text{标签有噪声时}\ \ \mathrm{GError}(f^*)>0", size=32),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        box = card(lines, pad=0.3).move_to([4.3, 1.45, 0])
        self.play_at(self.cue("真实"), FadeIn(box[0]), FadeIn(lines[0]), run_time=0.5)
        self.play_at(self.cue("理论上"), FadeIn(lines[1], shift=UP * 0.1), run_time=0.4)
        self.play_at(self.cue("只"), FadeIn(lines[2], shift=UP * 0.1), run_time=0.4)
        self.play_at(self.cue("标签"), FadeIn(lines[3], shift=UP * 0.1), run_time=0.5)

        # informal claim: closer to f* means less error
        l1 = Line(fig.pt(*STATIC_C), fs, color=WARN, stroke_width=7)
        l2 = Line(fig.pt(*P_OURS), fs, color=WARN, stroke_width=7)
        self.play_at(self.cue("离"), FadeOut(veil), ring.animate.scale(0.45), run_time=0.4)
        self.play(Create(l1), Create(l2), run_time=0.5)
        self.play(*[Indicate(l, color=ACCENT, scale_factor=1.0) for l in (l1, l2)], run_time=0.6)
        q1 = T("“Informally, closer to the true", size=24, slant=ITALIC)
        q2 = T("mapping leads to less error.”", size=24, slant=ITALIC)
        quote = VGroup(q1, q2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(box, DOWN, 0.4)
        inf = q1[1:11]
        ul = Underline(inf, color=ACCENT, stroke_width=4, buff=0.04)
        self.play_at(self.cue("作者"), FadeIn(quote), run_time=0.5)
        self.play_at(self.cue("非正式"), Create(ul), inf.animate.set_color(ACCENT), run_time=0.5)
        t1 = tag("示意图 ≠ 定理", color=WARN, size=24).next_to(quote, DOWN, 0.35)
        self.play_at(self.cue("示意图"), FadeIn(t1, scale=0.9), run_time=0.5)
        opt = T("另：图中 f* 画在假设空间内，等于默认模型能表示它，论文未论证", size=17, color=MUTED)
        opt.next_to(fig, DOWN, 0.18)
        self.play(FadeIn(opt), run_time=0.4)
