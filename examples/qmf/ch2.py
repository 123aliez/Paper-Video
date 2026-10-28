from common import *


def step_chips(active=None):
    names = ["① 凸性", "② 拆期望", "③ 单模态泛化界"]
    chips = VGroup()
    for i, n in enumerate(names):
        on = active == i
        t = T(n, size=22, color=BG if on else MUTED, weight=BOLD if on else NORMAL)
        b = RoundedRectangle(corner_radius=0.16, width=t.width + 0.45, height=0.46, stroke_width=1.5,
                             stroke_color=ACCENT if on else FAINT, fill_color=ACCENT if on else PANEL,
                             fill_opacity=1)
        chips.add(VGroup(b, t.move_to(b)))
    chips.arrange(RIGHT, buff=0.25).move_to([0, 2.95, 0])
    return chips


class S2_1(Shot):
    sid = "2-1"

    def body(self):
        defi = VGroup(TB("泛化误差", size=34, color=ACCENT), T("= 模型在新数据上的平均损失", size=32)).arrange(RIGHT, buff=0.2)
        defi.move_to([0, 2.55, 0])
        f1 = M(r"\mathrm{GError}(f)=\mathbb{E}_{(x,y)\sim\mathcal{D}}\big[\ell(f(x),y)\big]", size=42).next_to(defi, DOWN, 0.3)
        self.play_at(self.cue("模型"), FadeIn(defi, shift=DOWN * 0.15), run_time=0.6)
        self.play_at(self.cue("泛化误差"), Write(f1), run_time=0.9)

        # true error vs ceiling
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 5, 1], x_length=5.6, y_length=3.0, tips=False,
                  axis_config={"color": MUTED, "include_ticks": False}).move_to([-3.5, -1.15, 0])
        xl = T("不同的模型", size=18, color=MUTED).next_to(ax.x_axis, DOWN, 0.1)
        yl = T("误差", size=18, color=MUTED).next_to(ax.y_axis, UP, 0.1)
        true = ax.plot(lambda x: 1.3 + 0.5 * np.sin(x * 0.9) + 0.06 * x, x_range=[0.3, 9.7], color=INK)
        true_d = DashedVMobject(true, num_dashes=40)
        t_lab = T("真实误差（算不出来）", size=18, color=INK).move_to(ax.c2p(3.2, 0.45))
        ub = ax.plot(lambda x: 2.6 + 0.45 * np.sin(x * 0.9 + 0.3) + 0.08 * x, x_range=[0.3, 9.7], color=ACCENT)
        area = ax.get_area(ub, x_range=[0.3, 9.7], bounded_graph=ax.plot(lambda x: 5, x_range=[0.3, 9.7]),
                           color=ACCENT, opacity=0.18)
        u_lab = T("上界 = 天花板（可以算）", size=20, color=ACCENT).next_to(ax.c2p(5, 4.4), DOWN, 0.0)
        self.play_at(self.cue("没法"), Create(ax), FadeIn(xl), FadeIn(yl), Create(true_d), FadeIn(t_lab), run_time=0.9)
        self.play_at(self.cue("天花板"), FadeIn(area, shift=DOWN * 0.3), Create(ub), run_time=0.8)
        self.play_at(self.cue("上界"), FadeIn(u_lab), run_time=0.4)

        # setting
        head = TB("论文的设定（§3.2 Basic setting）", size=24, color=ACCENT)
        it1 = VGroup(T("• 二分类", size=24), M(r"y\in\{-1,\,1\}", size=34)).arrange(RIGHT, buff=0.25)
        it2 = VGroup(T("• logistic 损失", size=24), M(r"\ell(s,y)=\ln\!\big(1+e^{-ys}\big)", size=34)).arrange(RIGHT, buff=0.25)
        it2b = T("= 二分类交叉熵", size=22, color=TEAL)
        it3 = VGroup(T("• 加权求和的晚期融合", size=24)).arrange(RIGHT)
        it3b = M(r"f(x)=\sum_{m=1}^{M} w^m\, f^m\big(x^{(m)}\big)", size=34)
        col = VGroup(head, it1, it2, it2b, it3, it3b).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        it2b.shift(RIGHT * 0.35)
        it3b.shift(RIGHT * 0.35)
        col.move_to([3.45, -1.05, 0])
        note = T("logistic 损失式为标准形式，论文正文未写出", size=17, color=MUTED).next_to(col, DOWN, 0.15).align_to(col, LEFT)
        self.play_at(self.cue("论文"), FadeIn(head), run_time=0.4)
        self.play_at(self.cue("二分类"), FadeIn(it1, shift=LEFT * 0.15), run_time=0.4)
        self.play_at(self.cue("logistic"), FadeIn(it2, shift=LEFT * 0.15), FadeIn(note), run_time=0.5)
        self.play_at(self.cue("交叉"), FadeIn(it2b), run_time=0.4)
        self.play_at(self.cue("加权求和"), FadeIn(it3, shift=LEFT * 0.15), Write(it3b), run_time=0.8)


def loss(s):
    return np.log(1 + np.exp(-s))


class S2_2(Shot):
    sid = "2-2"

    def body(self):
        chips = step_chips()
        self.play_at(self.cue("推导"), FadeIn(chips, shift=DOWN * 0.15), run_time=0.5)
        self.play_at(self.cue("第一"), Transform(chips, step_chips(0)), run_time=0.4)
        src = self.source("附录 A.1 式 20")

        ax = Axes(x_range=[-3.5, 3.5, 1], y_range=[0, 3.5, 1], x_length=6.0, y_length=4.0, tips=False,
                  axis_config={"color": MUTED, "include_ticks": False}).move_to([-3.2, -0.55, 0])
        ax.y_axis.set_opacity(0)
        xl = M(r"s", size=30, color=MUTED).next_to(ax.x_axis, RIGHT, 0.1)
        curve = ax.plot(loss, x_range=[-3.3, 3.3], color=TEAL, stroke_width=5)
        c_lab = M(r"\ell(s)=\ln(1+e^{-s})\quad (y=+1)", size=28, color=TEAL).next_to(ax.c2p(-0.5, 3.4), UP, 0)
        convex = tag("凸函数：曲线向上弯", color=TEAL, size=20).next_to(ax.c2p(1.6, 2.2), UP, 0)
        self.play_at(self.cue("logistic"), Create(ax), FadeIn(xl), FadeIn(src), run_time=0.6)
        self.play_at(self.cue("凸函"), Create(curve), FadeIn(c_lab), run_time=0.9)
        self.play_at(self.cue("碗"), FadeIn(convex), run_time=0.4)

        s1, s2 = -2.6, 2.0
        p1, p2 = ax.c2p(s1, loss(s1)), ax.c2p(s2, loss(s2))
        d1, d2 = Dot(p1, color=INK), Dot(p2, color=INK)
        l1 = M(r"f^1", size=30).next_to(ax.c2p(s1, 0), DOWN, 0.1)
        l2 = M(r"f^2", size=30).next_to(ax.c2p(s2, 0), DOWN, 0.1)
        v1 = DashedLine(ax.c2p(s1, 0), p1, color=FAINT)
        v2 = DashedLine(ax.c2p(s2, 0), p2, color=FAINT)
        w = ValueTracker(0.5)

        def mix():
            return w.get_value() * s1 + (1 - w.get_value()) * s2

        on_curve = always_redraw(lambda: Dot(ax.c2p(mix(), loss(mix())), color=GOOD, radius=0.1))
        on_chord = always_redraw(lambda: Dot(ax.c2p(mix(), w.get_value() * loss(s1) + (1 - w.get_value()) * loss(s2)),
                                             color=ORANGE, radius=0.1))
        gap = always_redraw(lambda: Line(on_curve.get_center(), on_chord.get_center(), color=MUTED, stroke_width=3))
        chord = Line(p1, p2, color=ORANGE, stroke_width=3)
        lab_c = T("先混合再算损失", size=20, color=GOOD)
        lab_c.add_updater(lambda m: m.next_to(on_curve, RIGHT, 0.15).shift(DOWN * 0.28))
        lab_h = T("先算损失再混合", size=20, color=ORANGE)
        lab_h.add_updater(lambda m: m.next_to(on_chord, RIGHT, 0.15).shift(UP * 0.22))
        self.play_at(self.cue("先把"), FadeIn(d1, d2, l1, l2, v1, v2), run_time=0.4)
        self.play(FadeIn(on_curve, scale=1.5), FadeIn(lab_c), run_time=0.5)

        ineq = M(r"\ell\Big(\sum_{m} w^m f^m,\,y\Big)", r"\ \le\ ", r"\sum_{m} w^m\,\ell\big(f^m,\,y\big)", size=36)
        ineq[0].set_color(GOOD)
        ineq[2].set_color(ORANGE)
        ineq.move_to([3.55, 1.2, 0])
        self.play_at(self.cue("超过") - 0.3, Write(ineq[0]), Write(ineq[1]), run_time=0.6)
        self.play_at(self.cue("先算"), Create(chord), FadeIn(on_chord, scale=1.5), FadeIn(lab_h), Create(gap),
                     Write(ineq[2]), run_time=0.8)
        self.play(w.animate.set_value(0.2), run_time=0.8)
        self.play(w.animate.set_value(0.75), run_time=0.9)
        always = T("绿点始终在橙点下方", size=22, color=INK).next_to(ineq, DOWN, 0.35)
        self.play(FadeIn(always), w.animate.set_value(0.5), run_time=0.6)

        cond = M(r"\big(w^m\ge 0,\ \textstyle\sum_m w^m=1\big)", size=36, color=WARN).next_to(always, DOWN, 0.4)
        warn = tag("需要 w ≥ 0 且 Σw = 1（论文未写出）", color=WARN, size=22).next_to(cond, DOWN, 0.25)
        self.play_at(self.cue("要求"), Write(cond), run_time=0.7)
        self.play_at(self.cue("论文"), FadeIn(warn, shift=UP * 0.1), run_time=0.5)


class S2_3(Shot):
    sid = "2-3"

    def body(self):
        chips = step_chips(0)
        self.add(chips)
        self.play(Transform(chips, step_chips(1)), run_time=0.4)
        src = self.source("附录 A.1 式 21–23")
        e21 = M(r"\mathbb{E}\,\ell\big(f(x),y\big)\ \le\ \mathbb{E}\sum_{m=1}^{M} w^m\,\ell\big(f^m(x^{(m)}),y\big)", size=38)
        e22 = M(r"=\ \sum_{m=1}^{M}", r"\mathbb{E}\big[w^m\,\ell^m\big]", size=38)
        VGroup(e21, e22).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, 1.35, 0])
        e22.shift(RIGHT * 2.2)
        self.play_at(self.cue("两边"), Write(e21), FadeIn(src), run_time=1.0)
        self.play_at(self.cue("变成"), Write(e22), run_time=0.8)
        self.play(Indicate(e22[1], color=ACCENT), run_time=0.6)

        iden = M(r"\mathbb{E}\big[w^m \ell^m\big]", r"=", r"\mathbb{E}\big[w^m\big]\,\mathbb{E}\big[\ell^m\big]", r"+",
                 r"\mathrm{Cov}\big(w^m,\ell^m\big)", size=50).move_to([0, -1.0, 0])
        name = T("概率恒等式", size=22, color=MUTED).next_to(iden, UP, 0.3)
        self.play_at(self.cue("一条"), TransformFromCopy(e22[1], iden[0]), FadeIn(name), run_time=0.8)
        b0 = hl_box(iden[0], color=ACCENT)
        t0 = T("乘积的期望", size=22, color=ACCENT).next_to(b0, DOWN, 0.2)
        self.play_at(self.cue("乘积"), Create(b0), FadeIn(t0), run_time=0.5)
        self.play(Write(iden[1]), run_time=0.3)
        b1 = hl_box(iden[2], color=BASELINE)
        t1 = T("期望的乘积", size=22, color=BASELINE).next_to(b1, DOWN, 0.2)
        self.play_at(self.cue("期望的乘积") - 0.3, Write(iden[2]), run_time=0.6)
        self.play(Create(b1), FadeIn(t1), run_time=0.4)
        b2 = hl_box(iden[4], color=ORANGE)
        t2 = T("协方差", size=22, color=ORANGE).next_to(b2, DOWN, 0.2)
        self.play_at(self.cue("加上"), Write(iden[3]), Write(iden[4]), run_time=0.7)
        self.play(Create(b2), FadeIn(t2), run_time=0.4)


class S2_4(Shot):
    sid = "2-4"

    def body(self):
        chips = step_chips(1)
        self.add(chips)
        self.play(Transform(chips, step_chips(2)), run_time=0.4)
        uni = M(r"\mathbb{E}\big[\ell^m\big]", r"\le", r"\hat{E}(f^m)", r"+", r"\mathfrak{R}_m(f^m)", r"+",
                r"\sqrt{\frac{\ln(1/\delta)}{2N}}", size=46).move_to([0, 1.55, 0])
        src = self.source("附录 A.1（Bartlett & Mendelson, 2002）")
        self.play_at(self.cue("换成"), Write(uni), FadeIn(src), run_time=1.0)
        lab = [(2, "训练误差", BASELINE, "训练"), (4, "Rademacher 复杂度", PURPLE, "Rademacher"),
               (6, "尾项\n随 N 增大而变小", MUTED, "尾项")]
        braces = VGroup()
        for i, text, col, cue in lab:
            br = Brace(uni[i], DOWN, color=col)
            tl = T(text, size=20, color=col).next_to(br, DOWN, 0.08)
            if i == 6:
                tl.shift(RIGHT * 0.35)
            braces.add(VGroup(br, tl))
            self.play_at(self.cue(cue), uni[i].animate.set_color(col), GrowFromCenter(br), FadeIn(tl), run_time=0.5)

        # Rademacher intuition
        ax = Axes(x_range=[0, 9, 1], y_range=[-1.6, 1.6, 1], x_length=5.4, y_length=2.3, tips=False,
                  axis_config={"color": FAINT, "include_ticks": False}).move_to([-2.4, -1.45, 0])
        rng = np.random.default_rng(7)
        ys = rng.choice([-1, 1], 8)
        ys[0], ys[1] = 1, -1
        dots = VGroup(*[Dot(ax.c2p(i + 1, y), radius=0.09, color=GOOD if y > 0 else WARN) for i, y in enumerate(ys)])
        lbl = T("纯随机标签 ±1", size=20, color=MUTED).next_to(ax, UP, 0.05).align_to(ax, LEFT)
        simple = ax.plot(lambda x: 0.05 * (x - 4.5), x_range=[0.5, 8.5], color=INK, stroke_width=4)
        xs = np.arange(1, 9)

        def wig(x):
            # smooth interpolant through every random label
            return float(np.interp(x, xs, ys)) * 0.6 + 0.4 * float(np.sum([ys[i] * np.exp(-((x - xs[i]) ** 2) / 0.08) for i in range(8)]))

        wiggly = ax.plot(wig, x_range=[0.6, 8.4], color=INK, stroke_width=4)
        bar_bg = Rectangle(width=0.5, height=2.3, stroke_color=FAINT, stroke_width=2).move_to([1.3, -1.45, 0])
        level = ValueTracker(0.2)
        bar = always_redraw(lambda: Rectangle(width=0.5, height=2.3 * level.get_value(), stroke_width=0,
                                              fill_color=PURPLE, fill_opacity=0.9).align_to(bar_bg, DOWN).set_x(1.3))
        bar_l = T("复杂度", size=20, color=PURPLE).next_to(bar_bg, DOWN, 0.1)
        side = VGroup(T("简单模型：拟合不了", size=20, color=MUTED)).next_to(bar_bg, RIGHT, 0.4).shift(UP * 0.5)
        side2 = T("本事大：连随机标签都能背下", size=20, color=PURPLE).next_to(bar_bg, RIGHT, 0.4).shift(UP * 0.5)
        warn = tag("越可能在死记硬背", color=WARN, size=20).next_to(side2, DOWN, 0.3).align_to(side2, LEFT)
        self.play_at(self.cue("Rademacher", k=1), Create(ax), FadeIn(bar_bg), FadeIn(bar_l), FadeIn(bar), run_time=0.6)
        self.play_at(self.cue("拟合"), Create(simple), FadeIn(side), run_time=0.6)
        self.play_at(self.cue("随机"), LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.1), FadeIn(lbl), run_time=0.8)
        self.play_at(self.cue("本事", k=1), Transform(simple, wiggly), level.animate.set_value(0.92),
                     FadeTransform(side, side2), run_time=1.2)
        self.play_at(self.cue("死记硬背"), FadeIn(warn, shift=UP * 0.1), run_time=0.4)

        # Theorem 1
        self.play_at(self.cue("除"), *[FadeOut(m) for m in (ax, dots, lbl, simple, bar_bg, bar, bar_l, side2, warn, braces)],
                     uni.animate.scale(0.7).move_to([0, 2.2, 0]).set_opacity(0.45), run_time=0.6)
        thm = M(r"\mathrm{GError}(f) \le", r"\sum_{m=1}^{M} \mathbb{E}(w^m)\,\hat{E}(f^m)", r"+",
                r"\sum_{m=1}^{M} \mathbb{E}(w^m)\,\mathfrak{R}_m(f^m)", r"+",
                r"\sum_{m=1}^{M} \mathrm{Cov}(w^m,\ell^m)", r"+", r"M\sqrt{\frac{\ln(1/\delta)}{2N}}", size=40)
        thm.scale_to_fit_width(min(thm.width, 13.0)).move_to([0, 0.35, 0])
        name = TB("Theorem 1（式 2）", size=24, color=ACCENT).next_to(thm, UP, 0.45).align_to(thm, LEFT)
        prob = T("以至少 1 − δ 的概率成立", size=20, color=MUTED).next_to(name, RIGHT, 0.4)
        self.play(FadeIn(name), Write(thm), FadeIn(prob), run_time=1.2)
        thm[7].set_color(MUTED)
        parts = [(1, "Term-L", "损失项", BASELINE, "加权训练"), (3, "Term-C", "复杂度项", PURPLE, "加权复杂度"),
                 (5, "Term-Cov", "协方差项", ORANGE, "各路")]
        for i, en, zh, col, cue in parts:
            br = Brace(thm[i], DOWN, color=col)
            tl = VGroup(M(r"\text{" + en + "}", size=30, color=col), T(zh, size=22, color=col)).arrange(DOWN, buff=0.06)
            tl.next_to(br, DOWN, 0.1)
            self.play_at(self.cue(cue), thm[i].animate.set_color(col), GrowFromCenter(br), FadeIn(tl), run_time=0.6)
        self.play(Circumscribe(thm[5], color=ORANGE), run_time=0.8)


class S2_5(Shot):
    sid = "2-5"

    def body(self):
        name = TB("Theorem 2：动态 vs 静态的上界", size=26, color=ACCENT).move_to([-2.9, 2.95, 0])
        src = self.source("Theorem 2，式 4–6；附录 A.2")
        self.play_at(self.cue("定理"), FadeIn(name), FadeIn(src), run_time=0.5)
        p1 = VGroup(T("前提 1（式 5）", size=22, color=TEAL),
                    M(r"\mathbb{E}\big(w^m_{\text{dynamic}}\big) = w^m_{\text{static}}", size=34)).arrange(RIGHT, buff=0.3)
        p2 = VGroup(T("前提 2", size=22, color=TEAL), T("单模态网络结构相同", size=22),
                    M(r"\Rightarrow\ \hat{E},\ \mathfrak{R}\ \text{相同}", size=32)).arrange(RIGHT, buff=0.25)
        p2n = tag("论文据此认为（附录式 25–26）", color=MUTED, size=18, fill_opacity=0.05)
        prem = VGroup(p1, p2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-2.4, 1.95, 0]).align_to(name, LEFT)
        p2n.next_to(p2, RIGHT, 0.25)
        self.play_at(self.cue("式"), FadeIn(p1, shift=RIGHT * 0.15), run_time=0.6)
        self.play_at(self.cue("两边"), FadeIn(p2, shift=RIGHT * 0.15), run_time=0.6)
        self.play_at(self.cue("论文"), FadeIn(p2n), run_time=0.4)

        # comparison grid
        cw, rh = 2.6, 0.78
        x0, y0 = -6.4, 0.75
        heads = [T("", size=20), TB("静态", size=24, color=BASELINE), T("", size=20), TB("动态", size=24, color=ACCENT)]
        rows = [
            ("Term-L", BASELINE, r"\sum w^m_{\text{static}}\hat{E}(f^m)", "=", r"\sum \mathbb{E}(w^m_{\text{dyn}})\hat{E}(f^m)"),
            ("Term-C", PURPLE, r"\sum w^m_{\text{static}}\mathfrak{R}_m(f^m)", "=", r"\sum \mathbb{E}(w^m_{\text{dyn}})\mathfrak{R}_m(f^m)"),
            ("Term-Cov", ORANGE, r"0", r"\ge", r"\mathrm{Cov}(w^m_{\text{dyn}},\ell^m)\le 0"),
        ]
        xs = [x0 + 0.75, x0 + 3.0, x0 + 4.75, x0 + 6.5]
        hrow = VGroup(TB("静态", size=24, color=BASELINE).move_to([xs[1], y0, 0]),
                      TB("动态", size=24, color=ACCENT).move_to([xs[3], y0, 0]))
        grid = VGroup()
        cells = []
        for r, (nm, col, a, op, b) in enumerate(rows):
            y = y0 - (r + 1) * rh
            lab = M(r"\text{" + nm + "}", size=28, color=col).move_to([xs[0], y, 0])
            ca = M(a, size=28).move_to([xs[1], y, 0])
            co = M(op, size=34, color=GOOD).move_to([xs[2], y, 0])
            cb = M(b, size=28).move_to([xs[3], y, 0])
            cells.append((lab, ca, co, cb))
            grid.add(Line([x0, y + rh / 2, 0], [x0 + 8.1, y + rh / 2, 0], color=FAINT, stroke_width=1))
        self.play_at(self.cue("于是"), FadeIn(hrow), Create(grid),
                     *[FadeIn(VGroup(c[0], c[1], c[3])) for c in cells[:2]], FadeIn(cells[2][0]), run_time=0.7)
        self.play_at(self.cue("打平"), FadeIn(cells[0][2], scale=1.5), FadeIn(cells[1][2], scale=1.5), run_time=0.5)
        cov_row = SurroundingRectangle(VGroup(*cells[2]), color=ORANGE, buff=0.15, corner_radius=0.08)
        cov_row.stretch_to_fit_width(8.1).set_x(x0 + 4.05)
        self.play_at(self.cue("胜负手"), Create(cov_row), run_time=0.5)
        zero = VGroup(M(r"\mathrm{Cov}=0", size=28), T("常数", size=18, color=MUTED)).arrange(RIGHT, buff=0.15).move_to(cells[2][1])
        self.play_at(self.cue("常数"), FadeIn(zero), run_time=0.5)

        # scatter: loss vs weight
        sax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=3.3, y_length=2.6, tips=False,
                   axis_config={"color": MUTED, "include_ticks": False}).move_to([4.6, -0.15, 0])
        sxl = T("损失 ℓ", size=20, color=MUTED).next_to(sax.x_axis, DOWN, 0.1)
        syl = T("权重 w", size=20, color=MUTED).next_to(sax.y_axis, UP, 0.1)
        rng = np.random.default_rng(2)
        lx = rng.uniform(0.08, 0.92, 40)
        wy = np.clip(0.85 - 0.7 * lx + rng.normal(0, 0.08, 40), 0.05, 0.95)
        pts = VGroup(*[Dot(sax.c2p(a, b), radius=0.05, color=ACCENT) for a, b in zip(lx, wy)])
        fit = sax.plot(lambda x: 0.85 - 0.7 * x, x_range=[0.05, 0.95], color=ORANGE, stroke_width=3)
        rl = M(r"r<0", size=34, color=ORANGE).next_to(sax.c2p(0.95, 0.9), DOWN, 0).shift(LEFT * 0.2)
        self.play_at(self.cue("动态融合"), Create(sax), FadeIn(sxl), FadeIn(syl), run_time=0.5)
        self.play_at(self.cue("损失"), LaggedStart(*[FadeIn(p, scale=1.6) for p in pts], lag_ratio=0.03), run_time=1.2)
        self.play_at(self.cue("相关系数"), Create(fit), Write(rl), run_time=0.7)
        same = T("协方差与相关系数同号", size=20, color=MUTED).next_to(sxl, DOWN, 0.15)
        self.play_at(self.cue("同号") - 0.5, FadeIn(same), run_time=0.4)
        self.play_at(self.cue("上界", k=1), FadeIn(cells[2][3]), FadeIn(cells[2][2], scale=1.5), run_time=0.6)

        res = M(r"(5)\ \&\ (6)\ \Longrightarrow\ ", r"\mathcal{O}\big(\mathrm{GError}(f_{\text{dynamic}})\big)\le "
                r"\mathcal{O}\big(\mathrm{GError}(f_{\text{static}})\big)", r"\quad(4)", size=36)
        res.scale_to_fit_width(min(res.width, 8.2)).move_to([-2.35, -2.45, 0])
        rbox = SurroundingRectangle(res, color=ACCENT, buff=0.15, corner_radius=0.08)
        self.play_at(self.cue("真负相关"), Write(res), run_time=1.0)
        self.play(Create(rbox), run_time=0.4)


class S2_6(Shot):
    sid = "2-6"

    def body(self):
        def warn_card(num, title, w=6.1, h=4.0):
            box = RoundedRectangle(corner_radius=0.2, width=w, height=h, fill_color=PANEL, fill_opacity=1,
                                   stroke_color=WARN, stroke_width=2)
            n = TB(num, size=30, color=WARN)
            t = TB(title, size=26)
            head = VGroup(n, t).arrange(RIGHT, buff=0.2).next_to(box.get_top(), DOWN, 0.35)
            return VGroup(box, head)

        c1 = warn_card("①", "比的是上界，不是实际误差").move_to([-3.3, 0.25, 0])
        c2 = warn_card("②", "理论范围 ≠ 实验范围").move_to([3.3, 0.25, 0])
        self.play_at(self.cue("第一"), FadeIn(c1, shift=UP * 0.2), run_time=0.6)
        f = M(r"\mathcal{O}(\cdot)\ \neq\ \mathrm{GError}", size=36, color=ACCENT).next_to(c1[1], DOWN, 0.3)
        # ceiling drops, true error need not follow
        base = c1[0].get_bottom() + UP * 0.5
        floor = Line(base + LEFT * 2.3, base + RIGHT * 2.3, color=FAINT)
        hi = ValueTracker(2.0)
        ceil_ = always_redraw(lambda: Line(base + LEFT * 2.1 + UP * hi.get_value(), base + RIGHT * 2.1 + UP * hi.get_value(),
                                           color=ACCENT, stroke_width=5))
        ceil_l = always_redraw(lambda: T("上界（天花板）", size=18, color=ACCENT).next_to(ceil_, UP, 0.06))
        true = DashedLine(base + LEFT * 2.1 + UP * 0.9, base + RIGHT * 2.1 + UP * 0.9, color=INK)
        true_l = T("真实误差：不一定跟着降", size=18, color=INK).next_to(true, DOWN, 0.08)
        self.play_at(self.cue("上界"), Write(f), Create(floor), Create(ceil_), FadeIn(ceil_l), Create(true), FadeIn(true_l),
                     run_time=0.8)
        self.play_at(self.cue("天花板"), hi.animate.set_value(1.3), run_time=1.2)

        self.play_at(self.cue("第二"), FadeIn(c2, shift=UP * 0.2), run_time=0.6)
        th = VGroup(T("理论", size=24, color=TEAL), T("二分类 + logistic 损失", size=24)).arrange(RIGHT, buff=0.3)
        ex = VGroup(T("实验", size=24, color=ORANGE), T("多分类", size=24)).arrange(RIGHT, buff=0.3)
        VGroup(th, ex).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(c2[1], DOWN, 0.55)
        neq = M(r"\neq", size=44, color=WARN).move_to(VGroup(th, ex)).set_x(c2[0].get_right()[0] - 0.55)
        sm = T("NYU 10 类、SUN RGB-D 19 类（附录 B.1）", size=19, color=MUTED).next_to(ex, DOWN, 0.5).align_to(ex, LEFT)
        self.play_at(self.cue("理论"), FadeIn(th, shift=RIGHT * 0.1), run_time=0.5)
        self.play_at(self.cue("实验"), FadeIn(ex, shift=RIGHT * 0.1), FadeIn(neq), run_time=0.5)
        self.play_at(self.cue("比如"), FadeIn(sm), run_time=0.4)
        self.play_at(self.cue("10"), Indicate(sm, color=ACCENT, scale_factor=1.05), run_time=0.6)
