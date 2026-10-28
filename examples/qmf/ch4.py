from common import *
from ch1 import framed_image, node


class S4_1(Shot):
    sid = "4-1"

    def body(self):
        need = VGroup(T("理论要求：", size=24, color=MUTED), T("损失越大的一路，权重越小", size=24),
                      M(r"r(w,\ell)\le 0", size=32, color=ORANGE)).arrange(RIGHT, buff=0.2).move_to([0, 2.9, 0])
        self.play_at(self.cue("理论"), FadeIn(need, shift=DOWN * 0.1), run_time=0.6)

        img = framed_image("room_noise_5.png", 2.2).move_to([-4.6, 1.0, 0])
        cap = VGroup(T("测试样本", size=20, color=MUTED), T("标签：?", size=26, color=WARN)).arrange(DOWN, buff=0.1)
        cap.next_to(img, DOWN, 0.15)
        lossq = VGroup(T("损失", size=24, color=WARN), M(r"\ell", size=36, color=WARN), T("算不出", size=24, color=WARN))
        lossq.arrange(RIGHT, buff=0.12).next_to(cap, DOWN, 0.2)
        cross = Line(lossq.get_left(), lossq.get_right(), color=WARN, stroke_width=3).set_opacity(0)
        self.play_at(self.cue("测试"), FadeIn(img), FadeIn(cap), run_time=0.6)
        self.play_at(self.cue("算"), FadeIn(lossq), run_time=0.4)
        self.play(Create(cross), run_time=0.4)
        en = node("能量分数", 2.0, 0.7, ACCENT, 26).move_to([-1.3, -0.95, 0])
        arr = Arrow(lossq.get_right(), en.get_left(), buff=0.15, color=ACCENT, stroke_width=4)
        self.play_at(self.cue("QMF"), GrowArrow(arr), FadeIn(en, scale=0.9), run_time=0.7)

        # network -> logits
        net = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.32, height=1.6 - 0.25 * abs(i - 1.5),
                                        fill_color=BASELINE, fill_opacity=0.35 + 0.15 * i, stroke_color=BASELINE)
                       for i in range(4)]).arrange(RIGHT, buff=0.18).move_to([-0.1, 1.25, 0])
        net_l = T("单模态网络", size=20, color=MUTED).next_to(net, DOWN, 0.15)
        vals = [2.1, -0.4, 0.8]
        bars = VGroup()
        for v in vals:
            h = abs(v) * 0.55
            r = Rectangle(width=0.36, height=max(h, 0.02), stroke_width=0, fill_color=TEAL, fill_opacity=1)
            r.move_to(UP * (h / 2 if v > 0 else -h / 2))
            bars.add(r)
        bars.arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        for r, v in zip(bars, vals):
            if v < 0:
                r.shift(DOWN * r.height)
        base = Line(LEFT * 0.9, RIGHT * 0.9, color=MUTED, stroke_width=2)
        lg = VGroup(bars, base)
        base.move_to(bars[0].get_bottom()).set_x(bars.get_x())
        lg.move_to([2.55, 1.3, 0])
        nums = VGroup(*[M(f"{v}", size=24).next_to(r, UP if v > 0 else DOWN, 0.06) for r, v in zip(bars, vals)])
        lg_l = VGroup(T("logits", size=24, color=TEAL), T("还没过 softmax 的打分", size=18, color=MUTED)).arrange(DOWN, buff=0.06)
        lg_l.next_to(lg, DOWN, 0.35)
        a1 = Arrow(net.get_right(), lg.get_left(), buff=0.2, color=MUTED, stroke_width=3)
        sm = node("softmax → 概率", 2.2, 0.55, FAINT, 18).next_to(lg, RIGHT, 0.55)
        a2 = Arrow(lg.get_right(), sm.get_left(), buff=0.1, color=FAINT, stroke_width=3)
        self.play_at(self.cue("网络"), FadeIn(net), FadeIn(net_l), run_time=0.5)
        self.play(GrowArrow(a1), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), FadeIn(nums), run_time=0.8)
        self.play_at(self.cue("概率"), GrowArrow(a2), FadeIn(sm), run_time=0.5)
        self.play_at(self.cue("logits"), FadeIn(lg_l), Indicate(bars, color=TEAL), run_time=0.6)

        eq = M(r"\mathrm{Energy}\big(x^{(m)}\big) =", r"-\tau^m", r"\cdot", r"\log", r"\sum_{k=1}^{K}",
               r"e^{\,f^m_k(x^{(m)})/\tau^m}", size=46).move_to([2.05, -1.15, 0])
        self.play_at(self.cue("能量", k=1), FadeOut(arr), en.animate.move_to([-4.6, -2.3, 0]).scale(0.8), Write(eq[0]),
                     run_time=0.7)
        steps = [("负的温度", [1, 2], ORANGE), ("各类", [5], TEAL), ("取指数", [5], ACCENT), ("求和", [4], GOOD),
                 ("取对数", [3], PURPLE)]
        shown = {0}
        for cue, idx, col in steps:
            new = [i for i in idx if i not in shown]
            anims = [Write(eq[i]) for i in new] + [eq[i].animate.set_color(col) for i in idx if i in shown]
            self.play_at(self.cue(cue), *anims, run_time=0.6)
            if new:
                self.play(*[eq[i].animate.set_color(col) for i in new], run_time=0.2)
            shown.update(idx)
        knob = VGroup(Circle(radius=0.28, color=ORANGE, stroke_width=3), Line(ORIGIN, UP * 0.26, color=ORANGE, stroke_width=4))
        knob.next_to(eq, DOWN, 0.35).shift(LEFT * 1.5)
        kt = VGroup(M(r"\tau", size=34, color=ORANGE), T("温度：缩放打分的旋钮，论文取", size=20), M(r"\tau=1", size=32, color=ORANGE))
        kt.arrange(RIGHT, buff=0.15).next_to(knob, RIGHT, 0.25)
        note = T("论文式 13 记作 𝒯ᵐ；附录 B.2：τ = 1", size=18, color=MUTED).to_corner(UR, buff=0.36)
        self.play_at(self.cue("温度", k=2), FadeIn(knob), FadeIn(kt[0]), FadeIn(kt[1]), FadeIn(note), run_time=0.5)
        self.play(Rotate(knob[1], -PI / 2, about_point=knob[0].get_center()), run_time=0.6)
        self.play_at(self.cue("取 1") if "取 1" in self.text else self.cue("论文"), FadeIn(kt[2], scale=1.3), run_time=0.4)


def logit_group(vals, color, label):
    bars = VGroup()
    for v in vals:
        r = Rectangle(width=0.5, height=max(v * 0.36, 0.03), stroke_width=0, fill_color=color, fill_opacity=1)
        bars.add(r)
    bars.arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
    base = Line(LEFT * 1.2, RIGHT * 1.2, color=MUTED, stroke_width=2).move_to(bars.get_bottom())
    nums = VGroup(*[M(str(v), size=28).next_to(b, UP, 0.06) for b, v in zip(bars, vals)])
    ks = VGroup(*[M(f"k={i + 1}", size=20, color=MUTED).next_to(b, DOWN, 0.1) for i, b in enumerate(bars)])
    lab = T(label, size=22, color=color).next_to(ks, DOWN, 0.12)
    return VGroup(bars, base, nums, ks, lab)


class S4_2(Shot):
    sid = "4-2"

    def body(self):
        head = T("举例：三分类，温度 τ = 1", size=22, color=MUTED).move_to([-3.6, 2.95, 0])
        g1 = logit_group([5, 0, 0], GOOD, "干净照片：一类突起").move_to([-5.0, 1.45, 0])
        g2 = logit_group([1, 1, 1], WARN, "糊照片：各类平平").move_to([-2.0, 1.45, 0])
        VGroup(g1, g2).align_to(g1, DOWN)
        self.play_at(self.cue("举例"), FadeIn(head), run_time=0.4)
        self.play_at(self.cue("干净"), FadeIn(g1[1]), LaggedStart(*[GrowFromEdge(b, DOWN) for b in g1[0]], lag_ratio=0.2),
                     FadeIn(g1[3]), run_time=0.7)
        self.play_at(self.cue("5"), FadeIn(g1[2]), run_time=0.4)
        self.play_at(self.cue("一类"), FadeIn(g1[4]), Indicate(g1[0][0], color=GOOD), run_time=0.6)
        e1 = M(r"E_{\text{干净}} = -\log\big(e^{5}+e^{0}+e^{0}\big) = -\log 150.41 \approx", r"-5.01", size=30)
        e1[1].set_color(GOOD)
        e1.move_to([-3.35, -0.45, 0]).to_edge(LEFT, buff=0.45)
        self.play_at(self.cue("能量"), Write(e1), run_time=1.0)

        self.play_at(self.cue("糊"), FadeIn(g2[1]), LaggedStart(*[GrowFromEdge(b, DOWN) for b in g2[0]], lag_ratio=0.2),
                     FadeIn(g2[3]), FadeIn(g2[2]), run_time=0.7)
        self.play_at(self.cue("各类"), FadeIn(g2[4]), run_time=0.4)
        e2 = M(r"E_{\text{糊}} = -\log\big(3e^{1}\big) = -(1+\ln 3) \approx", r"-2.10", size=30)
        e2[1].set_color(WARN)
        e2.next_to(e1, DOWN, 0.3).align_to(e1, LEFT)
        self.play_at(self.cue("能量", k=1), Write(e2), run_time=1.0)

        nl = NumberLine(x_range=[-6, 0, 1], length=5.6, include_numbers=True, font_size=22, color=MUTED).move_to([3.7, 2.1, 0])
        nl_t = T("能量", size=20, color=MUTED).next_to(nl, LEFT, 0.2)
        m1 = VGroup(Triangle(color=GOOD, fill_opacity=1).scale(0.1).rotate(PI), T("干净 −5.01", size=18, color=GOOD))
        m1[1].next_to(m1[0], UP, 0.05)
        m1.next_to(nl.n2p(-5.01), UP, 0.05)
        m2 = VGroup(Triangle(color=WARN, fill_opacity=1).scale(0.1).rotate(PI), T("糊 −2.10", size=18, color=WARN))
        m2[1].next_to(m2[0], UP, 0.05)
        m2.next_to(nl.n2p(-2.10), UP, 0.05)
        hi = Arrow(nl.n2p(-4.6) + DOWN * 0.75, nl.n2p(-0.4) + DOWN * 0.75, buff=0, color=ACCENT, stroke_width=4)
        hi_t = T("越高 → 越拿不准", size=20, color=ACCENT).next_to(hi, DOWN, 0.08)
        self.play_at(self.cue("更"), Create(nl), FadeIn(nl_t), FadeIn(m1), FadeIn(m2), run_time=0.6)
        self.play_at(self.cue("即"), GrowArrow(hi), FadeIn(hi_t), run_time=0.5)

        eq9 = M(r"w^m(x) = \alpha^m", r"u^m(x)", r"+ \beta^m", r"\quad(\alpha^m<0,\ \beta^m\ge 0)", size=31)
        eq9.move_to([3.75, 0.15, 0])
        lab9 = T("式 9：权重是不确定度（这里用能量）的直线函数", size=18, color=MUTED).next_to(eq9, UP, 0.15)
        self.play_at(self.cue("权重"), Write(eq9[:3]), FadeIn(lab9), run_time=0.8)
        self.play_at(self.cue("负系数"), Write(eq9[3]), eq9[1].animate.set_color(ACCENT), run_time=0.6)
        sub = M(r"\alpha=-0.1,\ \ \beta=0", size=34, color=ORANGE).next_to(eq9, DOWN, 0.3)
        self.play_at(self.cue("设系"), Write(sub), run_time=0.6)
        w1 = M(r"w_{\text{干净}} = -0.1\times(-5.01)\approx", r"0.50", size=32)
        w1[1].set_color(GOOD)
        w2 = M(r"w_{\text{糊}} = -0.1\times(-2.10)\approx", r"0.21", size=32)
        w2[1].set_color(WARN)
        VGroup(w1, w2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(sub, DOWN, 0.28)
        self.play_at(self.cue("干净", k=1), Write(w1), run_time=0.8)
        self.play_at(self.cue("糊", k=1), Write(w2), run_time=0.8)
        warn = tag("α、β 为演示值，论文未报告", color=WARN, size=20).next_to(e2, DOWN, 0.35).align_to(e2, LEFT)
        self.play_at(self.cue("系数", k=2), FadeIn(warn, shift=UP * 0.1), run_time=0.5)


class S4_3(Shot):
    sid = "4-3"

    def body(self):
        src = self.source("Assumption 1 · Lemma 1")

        def chain_box(lines, col, w=3.4):
            g = VGroup(*lines).arrange(DOWN, buff=0.12)
            b = RoundedRectangle(corner_radius=0.15, width=w, height=g.height + 0.5, stroke_color=col, stroke_width=2.5,
                                 fill_color=col, fill_opacity=0.1)
            return VGroup(b, g.move_to(b))

        b1 = chain_box([M(r"u\uparrow\ \leftrightarrow\ \ell\uparrow", size=40), T("不确定度与损失正相关", size=20, color=MUTED),
                        T("假设 1", size=20, color=TEAL)], TEAL)
        b2 = chain_box([M(r"\times\,\alpha<0", size=40, color=ORANGE), T("乘上负系数", size=20, color=MUTED)], ORANGE, w=2.4)
        b3 = chain_box([M(r"w\downarrow\ \leftrightarrow\ \ell\uparrow", size=40), T("权重与损失负相关", size=20, color=MUTED),
                        T("式 6", size=20, color=ACCENT)], ACCENT)
        row = VGroup(b1, b2, b3).arrange(RIGHT, buff=0.8).move_to([0, 1.3, 0])
        b2.align_to(b1, UP).shift(DOWN * (b1.height - b2.height) / 2)
        a1 = Arrow(b1.get_right(), b2.get_left(), buff=0.1, color=MUTED)
        a2 = Arrow(b2.get_right(), b3.get_left(), buff=0.1, color=MUTED)
        self.play_at(self.cue("只要"), FadeIn(b1[0]), FadeIn(b1[1][:2]), FadeIn(src), run_time=0.6)
        self.play_at(self.cue("假设"), FadeIn(b1[1][2], scale=1.3), run_time=0.4)
        self.play_at(self.cue("乘上"), GrowArrow(a1), FadeIn(b2), run_time=0.6)
        self.play_at(self.cue("权重"), GrowArrow(a2), FadeIn(b3), run_time=0.6)

        f = M(r"r\big(u^m,\ell^m\big)\ge 0\ \ \xrightarrow{\ \alpha^m<0\ }\ \ r\big(w^m,\ell^m\big) = -\,r\big(u^m,\ell^m\big)\le 0", size=36)
        f.move_to([0, -0.55, 0])
        self.play(Write(f), run_time=0.9)
        knob = VGroup(Circle(radius=0.32, color=GOOD, stroke_width=3), Line(ORIGIN, UP * 0.3, color=GOOD, stroke_width=4))
        kl = M(r"\beta", size=34, color=GOOD).next_to(knob, LEFT, 0.15)
        res = VGroup(T("调常数 β", size=22), M(r"\Rightarrow\ \mathbb{E}(w)=w_{\text{static}}", size=36, color=GOOD),
                     T("（式 5）", size=20, color=MUTED)).arrange(RIGHT, buff=0.2)
        grp = VGroup(kl, knob, res).arrange(RIGHT, buff=0.25).move_to([0, -1.85, 0])
        self.play_at(self.cue("再调"), FadeIn(kl), FadeIn(knob), FadeIn(res[0]), run_time=0.4)
        self.play(Rotate(knob[1], -2 * PI / 3, about_point=knob[0].get_center()), run_time=0.7)
        self.play_at(self.cue("满足"), Write(res[1]), FadeIn(res[2]), run_time=0.6)


# ---- training-loss chart shared by 4-4 and 4-5
EPOCHS = 30


def clean_loss(t):
    return 2.2 * np.exp(-t / 2.5) + 0.03


def noisy_loss(t):
    return 2.3 / (1 + np.exp((t - 14) / 2.2)) + 0.05


def training_chart():
    ax = Axes(x_range=[0, EPOCHS, 5], y_range=[0, 2.6, 1], x_length=6.4, y_length=4.0, tips=False,
              axis_config={"color": MUTED, "include_ticks": False}).move_to([-3.1, -0.35, 0])
    xl = T("epoch", size=20, color=MUTED).next_to(ax.x_axis, DOWN, 0.12).align_to(ax.x_axis, RIGHT)
    yl = T("当期损失", size=20, color=MUTED).next_to(ax.y_axis, UP, 0.12)
    c1 = ax.plot(clean_loss, x_range=[1, EPOCHS], color=GOOD, stroke_width=5)
    c2 = ax.plot(noisy_loss, x_range=[1, EPOCHS], color=WARN, stroke_width=5)
    l1 = T("干净样本", size=20, color=GOOD).next_to(ax.c2p(3.6, clean_loss(3.6)), UR, 0.08)
    l2 = T("噪声样本", size=20, color=WARN).next_to(ax.c2p(13, noisy_loss(13)), UR, 0.1)
    note = T("示意曲线，不是论文数据", size=17, color=MUTED).next_to(ax, DOWN, 0.42).align_to(ax, LEFT)
    return ax, xl, yl, c1, c2, l1, l2, note


def last_epoch_marks(ax):
    vl = DashedLine(ax.c2p(EPOCHS, 0), ax.c2p(EPOCHS, 2.5), color=ACCENT, stroke_width=3)
    q = TB("?", size=60, color=ACCENT).next_to(ax.c2p(EPOCHS, 1.3), RIGHT, 0.2)
    ql = T("最后一个 epoch", size=18, color=ACCENT).next_to(ax.c2p(EPOCHS, 2.5), UP, 0.1)
    return vl, q, ql


def question_text():
    return VGroup(T("想一想：", size=26, color=ACCENT),
                  T("只在最后一个 epoch 记录，", size=26), T("会怎样？", size=26)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([3.9, 0.6, 0])


class S4_4(Shot):
    sid = "4-4"
    carry_out = True

    def body(self):
        weak = tag("只靠能量：相关性不够强（Table 3）", color=MUTED, size=20, fill_opacity=0.05).move_to([0, 2.85, 0])
        self.play_at(self.cue("只"), FadeIn(weak), run_time=0.5)
        total = T("总损失", size=30).move_to([-4.6, 1.2, 0])
        eqs = T("=", size=34).next_to(total, RIGHT, 0.3)
        ce = node("交叉熵", 2.2, 0.9, BASELINE, 28).next_to(eqs, RIGHT, 0.3)
        plus = T("+", size=34).next_to(ce, RIGHT, 0.3)
        reg = node("正则项", 2.2, 0.9, ACCENT, 28).next_to(plus, RIGHT, 0.3)
        self.play_at(self.cue("作者"), FadeIn(total), FadeIn(eqs), FadeIn(ce), run_time=0.6)
        self.play_at(self.cue("交叉熵"), Indicate(ce, color=BASELINE), run_time=0.5)
        self.play_at(self.cue("加一"), FadeIn(plus), FadeIn(reg, shift=LEFT * 0.2), run_time=0.6)
        d1 = T("一项可求导的惩罚", size=20, color=ACCENT).next_to(reg, DOWN, 0.2)
        self.play_at(self.cue("可求导"), FadeIn(d1), run_time=0.4)
        knob = VGroup(Circle(radius=0.3, color=ACCENT, stroke_width=3), Line(ORIGIN, UP * 0.28, color=ACCENT, stroke_width=4))
        knob.next_to(reg, RIGHT, 0.45)
        kt = T("按需设计", size=22, color=ACCENT).next_to(knob, RIGHT, 0.15)
        push = T("把模型推向想要的性质", size=22, color=MUTED).next_to(d1, DOWN, 0.2)
        self.play_at(self.cue("推向"), FadeIn(push), run_time=0.4)
        self.play_at(self.cue("按需"), FadeIn(knob), FadeIn(kt), run_time=0.4)
        self.play(Rotate(knob[1], -PI / 2, about_point=knob[0].get_center()), run_time=0.6)
        want = VGroup(T("这里要的：", size=24, color=MUTED), T("历来越难学的样本，权重越小", size=28, color=ACCENT)).arrange(RIGHT, buff=0.2)
        want.move_to([0, -0.75, 0])
        f15 = M(r"\kappa_i^m \ge \kappa_j^m \iff w_i^m \le w_j^m\quad(15)", size=36).next_to(want, DOWN, 0.3)
        self.play_at(self.cue("这里"), FadeIn(want[0]), run_time=0.4)
        self.play_at(self.cue("历来"), FadeIn(want[1], shift=UP * 0.1), run_time=0.5)
        self.play_at(self.cue("权重"), Write(f15), run_time=0.8)

        # why "historical": training curves
        stage = VGroup(weak, total, eqs, ce, plus, reg, d1, knob, kt, push, want, f15)
        ax, xl, yl, c1, c2, l1, l2, note = training_chart()
        self.play_at(self.cue("为何"), FadeOut(stage), run_time=0.5)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(note), run_time=0.6)
        self.play_at(self.cue("深度网"), Create(c1), FadeIn(l1), run_time=1.0)
        self.play_at(self.cue("训练样本"), Create(c2), FadeIn(l2), run_time=1.2)
        op = VGroup(TB("过参数化", size=28, color=PURPLE), T("参数多到能背下全部训练样本，", size=22),
                    T("包括脏的", size=22, color=WARN)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([3.8, 1.2, 0])
        self.play_at(self.cue("包括"), FadeIn(op[1:], shift=LEFT * 0.1), run_time=0.5)
        self.play_at(self.cue("过参数化"), FadeIn(op[0], scale=1.2), run_time=0.5)
        late = Rectangle(width=ax.c2p(EPOCHS, 0)[0] - ax.c2p(20, 0)[0], height=4.0, stroke_width=0,
                         fill_color=PURPLE, fill_opacity=0.12)
        late.move_to(ax.c2p(25, 1.3))
        late_t = T("后期：都 ≈ 0", size=20, color=PURPLE).next_to(late, UP, 0.05)
        self.play_at(self.cue("后期"), FadeIn(late), FadeIn(late_t), run_time=0.6)
        vl, q, ql = last_epoch_marks(ax)
        qt = question_text()
        self.play_at(self.cue("想一想"), FadeOut(op), FadeOut(late), FadeOut(late_t), run_time=0.4)
        self.play(FadeIn(qt[0]), run_time=0.3)
        self.play_at(self.cue("只在"), Create(vl), FadeIn(ql), FadeIn(qt[1:]), run_time=0.6)
        self.play(FadeIn(q, scale=1.4), run_time=0.4)


class S4_5(Shot):
    sid = "4-5"
    carry_in = True

    def body(self):
        ax, xl, yl, c1, c2, l1, l2, note = training_chart()
        vl, q, ql = last_epoch_marks(ax)
        qt = question_text()
        self.add(ax, xl, yl, c1, c2, l1, l2, note, vl, q, ql, qt)
        d1 = Dot(ax.c2p(EPOCHS, clean_loss(EPOCHS)), color=GOOD, radius=0.09)
        d2 = Dot(ax.c2p(EPOCHS, noisy_loss(EPOCHS)), color=WARN, radius=0.09)
        ans = VGroup(T("两者都 ≈ 0", size=26), T("→ 正则项拿不到信号", size=26, color=WARN)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        ans.move_to(qt, aligned_edge=UL)
        self.play_at(self.cue("都"), FadeIn(d1, scale=2), FadeIn(d2, scale=2), FadeOut(q), FadeOut(qt), FadeIn(ans[0]), run_time=0.6)
        self.play_at(self.cue("信号"), FadeIn(ans[1], shift=UP * 0.1), run_time=0.4)

        a1 = ax.get_area(c1, x_range=[1, EPOCHS], color=GOOD, opacity=0.35)
        a2 = ax.get_area(c2, x_range=[1, EPOCHS], color=WARN, opacity=0.25)
        e14 = M(r"\kappa_i^m = \frac{1}{S}\sum_{t=T_s}^{T_s+S} \ell\big(y_i,\ f^m_{\theta_t}(x_i)\big),\qquad T_s = 1", size=34)
        e14.move_to([3.6, -0.55, 0])
        n14 = T("论文式 14 记作 T；附录 B.2：Tₛ = 1，全程采样；S 的具体数值论文未给", size=17, color=MUTED)
        n14.to_corner(UR, buff=0.36)
        self.play_at(self.cue("所以"), FadeOut(ans), FadeOut(vl), FadeOut(ql), FadeOut(d1), FadeOut(d2), run_time=0.4)
        e1 = Line(ax.c2p(1, 0), ax.c2p(1, 2.5), color=TEAL, stroke_width=3)
        e1l = T("第 1 个 epoch 起", size=18, color=TEAL).next_to(ax.c2p(1, 0), DOWN, 0.12).shift(RIGHT * 0.5)
        self.play_at(self.cue("从第"), Create(e1), FadeIn(e1l), run_time=0.5)
        self.play_at(self.cue("全程"), FadeIn(a2), FadeIn(a1), run_time=0.8)
        self.play_at(self.cue("平均"), Write(e14), FadeIn(n14), run_time=1.0)
        k1 = T("学得早 → κ 小", size=22, color=GOOD).move_to([2.2, 1.75, 0], aligned_edge=LEFT)
        k2 = T("学得晚 → κ 大", size=22, color=WARN).next_to(k1, DOWN, 0.2, aligned_edge=LEFT)
        self.play_at(self.cue("简单"), FadeIn(k1, shift=LEFT * 0.1), Indicate(a1, color=GOOD, scale_factor=1.0), run_time=0.6)
        self.play_at(self.cue("难"), FadeIn(k2, shift=LEFT * 0.1), Indicate(a2, color=WARN, scale_factor=1.0), run_time=0.6)
        kk = tag("κ 记下的是：多久才学会", color=ACCENT, size=22).next_to(e14, DOWN, 0.4)
        self.play_at(self.cue("记下"), FadeIn(kk, scale=0.9), run_time=0.5)


class S4_6(Shot):
    sid = "4-6"

    def body(self):
        e16 = M(r"\mathcal{L}_{\text{reg}} =", r"\max\Big(0,\ ", r"g\big(w_i^m,w_j^m\big)\big(\kappa_i^m-\kappa_j^m\big)", r"+",
                r"\big|w_i^m-w_j^m\big|", r"\Big)", size=38)
        e17 = M(r"g = \begin{cases} 1 & w_i^m > w_j^m \\ 0 & w_i^m = w_j^m \\ -1 & \text{otherwise} \end{cases}", size=30)
        top = VGroup(e16, e17).arrange(RIGHT, buff=0.6).move_to([0, 2.35, 0])
        gn = T("g：看谁的权重大", size=18, color=TEAL).next_to(e17, DOWN, 0.08)
        src = self.source("式 16–17")
        self.play_at(self.cue("正"), Write(e16), FadeIn(src), run_time=1.0)
        self.play(FadeIn(e17), FadeIn(gn), run_time=0.5)
        self.play_at(self.cue("权重较大"), e16[2].animate.set_color(TEAL), run_time=0.4)
        self.play_at(self.cue("加上"), e16[4].animate.set_color(ORANGE), run_time=0.4)
        self.play_at(self.cue("再和"), e16[1].animate.set_color(ACCENT), e16[5].animate.set_color(ACCENT), run_time=0.4)

        # two samples
        base_y = -2.55
        H = 2.6

        def wbar(x, w, col):
            r = Rectangle(width=0.8, height=w * H, stroke_width=0, fill_color=col, fill_opacity=0.85)
            return r.move_to([x, base_y + w * H / 2, 0])

        xa, xb = -5.0, -2.6
        ca = VGroup(TB("甲", size=28, color=GOOD), M(r"\kappa=0.2", size=30)).arrange(RIGHT, buff=0.2).move_to([xa, 1.05, 0])
        cb = VGroup(TB("乙", size=28, color=WARN), M(r"\kappa=1.0", size=30)).arrange(RIGHT, buff=0.2).move_to([xb, 1.05, 0])
        base = Line([xa - 0.9, base_y, 0], [xb + 0.9, base_y, 0], color=MUTED)
        self.play_at(self.cue("甲"), FadeIn(ca, shift=DOWN * 0.1), run_time=0.4)
        self.play_at(self.cue("乙"), FadeIn(cb, shift=DOWN * 0.1), run_time=0.4)
        wa, wb = ValueTracker(0.7), ValueTracker(0.4)
        ba = always_redraw(lambda: wbar(xa, wa.get_value(), GOOD))
        bb = always_redraw(lambda: wbar(xb, wb.get_value(), WARN))
        la = always_redraw(lambda: M(rf"w={wa.get_value():.2f}", size=28).next_to(ba, UP, 0.08))
        lb = always_redraw(lambda: M(rf"w={wb.get_value():.2f}", size=28).next_to(bb, UP, 0.08))
        s1 = tag("顺序对：κ 小的权重大", color=GOOD, size=20).move_to([2.8, 0.95, 0])
        self.play_at(self.cue("顺序"), Create(base), FadeIn(ba), FadeIn(bb), FadeIn(la), FadeIn(lb), FadeIn(s1), run_time=0.6)
        c1 = M(r"1\times(0.2-1.0)+0.3", r"=-0.5", size=36).move_to([2.8, 0.1, 0])
        c1b = M(r"\Rightarrow\ \mathcal{L}_{\text{reg}}=\max(0,-0.5)=0,\ \ \nabla=0", size=34, color=GOOD).next_to(c1, DOWN, 0.25)
        self.play_at(self.cue("0.2 减"), Write(c1[0]), run_time=1.2)
        self.play_at(self.cue("得"), Write(c1[1]), run_time=0.5)
        self.play_at(self.cue("取零"), Write(c1b), run_time=0.8)
        zero_g = T("无梯度：权重不动", size=22, color=GOOD).next_to(c1b, DOWN, 0.2)
        self.play_at(self.cue("无"), FadeIn(zero_g), run_time=0.4)

        # reversed order
        s2 = tag("顺序反：κ 大的权重反而大", color=WARN, size=20).move_to(s1)
        self.play_at(self.cue("顺序", k=1), FadeOut(c1), FadeOut(c1b), FadeOut(zero_g), FadeTransform(s1, s2),
                     wa.animate.set_value(0.4), wb.animate.set_value(0.7), run_time=0.8)
        c2 = M(r"(-1)\times(0.2-1.0)+0.3", r"=1.1", size=36).move_to([2.8, 0.1, 0])
        c2b = M(r"\frac{\partial\mathcal{L}_{\text{reg}}}{\partial w_{\text{甲}}}=-1,\qquad \frac{\partial\mathcal{L}_{\text{reg}}}{\partial w_{\text{乙}}}=+1",
                size=34, color=WARN).next_to(c2, DOWN, 0.25)
        self.play_at(self.cue("1.0 减"), Write(c2[0]), run_time=1.2)
        self.play_at(self.cue("得", k=1), Write(c2[1]), run_time=0.5)
        ga = Arrow(ORIGIN, UP * 0.9, buff=0, color=ACCENT, stroke_width=6)
        gb = Arrow(ORIGIN, DOWN * 0.9, buff=0, color=ACCENT, stroke_width=6)
        ga.add_updater(lambda m: m.next_to(ba, RIGHT, 0.12).align_to(ba, DOWN).shift(UP * 0.1))
        gb.add_updater(lambda m: m.next_to(bb, RIGHT, 0.12).align_to(bb, UP).shift(DOWN * 0.1))
        self.play_at(self.cue("梯度", k=1), Write(c2b), GrowArrow(ga), GrowArrow(gb), run_time=0.7)
        self.play(wa.animate.set_value(0.56), wb.animate.set_value(0.54), run_time=1.6)
        done = T("直到不再颠倒", size=22, color=ACCENT).next_to(c2b, DOWN, 0.25)
        self.play_at(self.cue("直到"), FadeIn(done), run_time=0.4)


class S4_7(Shot):
    sid = "4-7"

    def body(self):
        names = [("θᵐ 单模态网络", BASELINE), ("logits", TEAL), ("能量（式 13）", PURPLE), ("权重 w（式 9）", ACCENT),
                 ("正则罚分", ORANGE)]
        nodes = VGroup(*[node(n, 2.25, 0.75, c, 22) for n, c in names]).arrange(RIGHT, buff=0.42).move_to([0, 1.55, 0])
        lreg = M(r"\mathcal{L}_{\text{reg}}", size=30, color=ORANGE).next_to(nodes[4], UP, 0.12)
        nodes[4].add(lreg)
        fw = VGroup(*[Arrow(nodes[i].get_right(), nodes[i + 1].get_left(), buff=0.06, color=MUTED, stroke_width=3)
                      for i in range(4)])
        self.play_at(self.cue("权重"), FadeIn(nodes[3]), FadeIn(nodes[4]), GrowArrow(fw[3]), run_time=0.5)
        self.play(FadeIn(nodes[2]), GrowArrow(fw[2]), run_time=0.4)
        self.play_at(self.cue("能量", k=1), FadeIn(nodes[1]), GrowArrow(fw[1]), run_time=0.4)
        self.play_at(self.cue("logits"), FadeIn(nodes[0]), GrowArrow(fw[0]), run_time=0.4)
        y_b = nodes[0][0].get_bottom()[1] - 0.45
        bw = Arrow([nodes[4].get_center()[0], y_b, 0], [nodes[0].get_center()[0], y_b, 0], buff=0, color=WARN,
                   stroke_width=6, max_tip_length_to_length_ratio=0.03)
        bl = T("反向传播：罚分一路传回单模态网络参数", size=22, color=WARN).next_to(bw, DOWN, 0.2)
        self.play_at(self.cue("所以"), GrowArrow(bw), FadeIn(bl),
                     LaggedStart(*[nodes[i][0].animate.set_stroke(WARN, width=4) for i in (4, 3, 2, 1, 0)], lag_ratio=0.4),
                     run_time=1.8)
        self.play_at(self.cue("单模态", k=1), Indicate(nodes[0], color=BASELINE, scale_factor=1.12), run_time=0.7)

        e18 = M(r"\mathcal{L}_{\text{overall}} =", r"\mathcal{L}_{\text{CE}}\big(y,f(x)\big)", r"+",
                r"\sum_{m=1}^{M}\mathcal{L}_{\text{CE}}\big(y,f^m(x^{(m)})\big)", r"+", r"\lambda\,\mathcal{L}_{\text{reg}}", size=40)
        e18.move_to([0, -1.55, 0])
        lam = T("λ = 0.1（附录 B.2）", size=20, color=ORANGE).next_to(e18[5], DOWN, 0.2)
        self.play_at(self.cue("总"), Write(e18[0]), run_time=0.4)
        self.play_at(self.cue("融合"), Write(e18[1]), e18[1].animate.set_color(ACCENT), run_time=0.6)
        self.play_at(self.cue("各"), Write(e18[2:4]), run_time=0.7)
        self.play_at(self.cue("0.1"), Write(e18[4:]), FadeIn(lam), run_time=0.7)
        self.play(e18[5].animate.set_color(ORANGE), run_time=0.3)
