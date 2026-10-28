from common import *
from ch1 import stacked_table1

BOX3 = json.loads((ASSETS / "fig3_boxes.json").read_text())
F3_TICK_Y = (1185, 1265)
F3_XS = [549, 1014, 1476, 1941]


class S5_1(Shot):
    sid = "5-1"

    def body(self):
        fig = Crop("fig3b.png", (0, 0, 2205, 1429), height=3.7, scale_px=2.0).move_to([3.75, 0.35, 0])
        cap = T("Figure 3(b) SUN RGB-D", size=18, color=MUTED).next_to(fig, DOWN, 0.12)
        src = self.source("Figure 3 图注：10 次随机实验")
        self.play_at(self.cue("实验"), FadeIn(fig, shift=UP * 0.15), FadeIn(cap), FadeIn(src), run_time=0.6)

        # schematic box plot built from 10 runs
        vals = np.array([0.30, 0.52, 0.55, 0.58, 0.60, 0.62, 0.64, 0.67, 0.72, 0.78])
        q1, med, q3 = 0.556, 0.61, 0.665
        ax = Axes(x_range=[0, 1, 1], y_range=[0.2, 0.9, 0.1], x_length=2.2, y_length=4.6, tips=False,
                  axis_config={"color": FAINT, "include_ticks": False}).move_to([-5.6, 0.15, 0])
        ax.x_axis.set_opacity(0)
        dots = VGroup(*[Dot(ax.c2p(0.18 + 0.04 * (i % 3), v), radius=0.07, color=TEAL) for i, v in enumerate(vals)])
        runs = T("10 次随机种子 → 10 个结果", size=20, color=TEAL).next_to(ax, UP, 0.1).align_to([-6.6, 0, 0], LEFT)
        box = Rectangle(width=1.1, height=ax.c2p(0, q3)[1] - ax.c2p(0, q1)[1], stroke_color=INK, stroke_width=3,
                        fill_color=ORANGE, fill_opacity=0.6).move_to(ax.c2p(0.62, (q1 + q3) / 2))
        mline = Line(ax.c2p(0.62, med) + LEFT * 0.55, ax.c2p(0.62, med) + RIGHT * 0.55, color=INK, stroke_width=5)
        wl = VGroup(Line(ax.c2p(0.62, q3), ax.c2p(0.62, 0.78)), Line(ax.c2p(0.62, 0.78) + LEFT * 0.3, ax.c2p(0.62, 0.78) + RIGHT * 0.3),
                    Line(ax.c2p(0.62, q1), ax.c2p(0.62, 0.52)), Line(ax.c2p(0.62, 0.52) + LEFT * 0.3, ax.c2p(0.62, 0.52) + RIGHT * 0.3))
        wl.set_stroke(INK, 3)
        out = Circle(radius=0.08, color=INK, stroke_width=3).move_to(ax.c2p(0.62, 0.30))
        self.play_at(self.cue("Figure"), Create(ax), run_time=0.4)
        self.play_at(self.cue("每"), FadeIn(runs), LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.08), run_time=0.9)

        def label(text, target_pt, col):
            t = T(text, size=22, color=col)
            t.move_to([-3.85, target_pt[1], 0], aligned_edge=LEFT)
            a = Arrow(t.get_left() + LEFT * 0.05, target_pt + RIGHT * 0.05, buff=0.05, color=col, stroke_width=3,
                      max_tip_length_to_length_ratio=0.15)
            return VGroup(a, t)

        l1 = label("箱体 = 中间 50% 的结果", box.get_right() + UP * 0.22, ORANGE)
        l2 = label("横线 = 中位数", mline.get_right(), INK)
        l2[1].shift(DOWN * 0.45)
        l2[0].put_start_and_end_on(l2[1].get_left() + LEFT * 0.05, mline.get_right() + RIGHT * 0.05)
        l3 = label("须线 = 非离群范围", ax.c2p(0.62, 0.75) + RIGHT * 0.3, MUTED)
        l4 = label("圆点 = 离群点", out.get_right(), WARN)
        self.play_at(self.cue("箱体"), FadeIn(box), dots.animate.set_opacity(0.35), FadeIn(l1), run_time=0.6)
        self.play_at(self.cue("横线"), Create(mline), FadeIn(l2), run_time=0.5)
        self.play_at(self.cue("须线"), Create(wl), FadeIn(l3), run_time=0.5)
        real = Circle(radius=0.16, color=WARN, stroke_width=4).move_to(fig.pt(1479, 630))
        self.play_at(self.cue("圆点"), Create(out), FadeIn(l4), Create(real), run_time=0.6)


class S5_2(Shot):
    sid = "5-2"

    def body(self):
        fa = Crop("fig3a.png", (0, 0, 2205, 1430), height=3.75, scale_px=2.0)
        fb = Crop("fig3b.png", (0, 0, 2205, 1429), height=3.75, scale_px=2.0)
        Group(fa, fb).arrange(RIGHT, buff=0.35).move_to([0, 0.72, 0])
        ca = T("(a) NYU Depth V2", size=18, color=MUTED).next_to(fa, UP, 0.08)
        cb = T("(b) SUN RGB-D", size=18, color=MUTED).next_to(fb, UP, 0.08)
        src = self.source("出处：Figure 3")
        self.play_at(self.cue("横轴"), FadeIn(fa), FadeIn(fb), FadeIn(ca), FadeIn(cb), FadeIn(src), run_time=0.6)
        xa = fa.rect((250, 1280, 2000, 1420), color=ACCENT, fill=0.12, width=3, pad=0)
        xb = fb.rect((250, 1280, 2000, 1420), color=ACCENT, fill=0.12, width=3, pad=0)
        xt = T("横轴：权重与损失的相关系数", size=20, color=ACCENT).next_to(Group(fa, fb), DOWN, 0.15)
        self.play_at(self.cue("权重"), Create(xa), Create(xb), FadeIn(xt), run_time=0.6)

        names = [("Static", "静态", "静态"), ("MSP", "最大预测概率加权", "最大预测"), ("Ours", "能量加权", "能量加权"),
                 ("Ours (Reg)", "能量加正则", "能量加正则")]
        cols = ["#E07B5F", "#3D405B", "#81B29A", "#F2CC8F"]
        leg = VGroup()
        for (en, zh, _), c in zip(names, cols):
            leg.add(VGroup(Square(0.22, fill_color=c, fill_opacity=1, stroke_color=WHITE, stroke_width=1),
                           T(f"{en} = {zh}", size=19)).arrange(RIGHT, buff=0.1))
        leg.arrange(RIGHT, buff=0.35).move_to([0, -1.75, 0])
        self.play_at(self.cue("四"), FadeOut(xa), FadeOut(xb), FadeOut(xt), run_time=0.3)
        boxes_a, boxes_b = [], []
        for k, (en, zh, cue) in enumerate(names):
            x = F3_XS[k]
            ba = fa.rect((x - 120, 300, x + 120, 1190), color=WHITE, fill=0.0, width=3, pad=0)
            bb = fb.rect((x - 120, 120, x + 120, 1190), color=WHITE, fill=0.0, width=3, pad=0)
            boxes_a.append(ba)
            boxes_b.append(bb)
            self.play_at(self.cue(cue), FadeIn(leg[k], shift=UP * 0.1), Create(ba), Create(bb), run_time=0.45)
            self.play(FadeOut(ba), FadeOut(bb), run_time=0.25)

        def tick_seq(f, cue_word):
            rs = [f.rect((x - 110, F3_TICK_Y[0], x + 110, F3_TICK_Y[1]), color=ACCENT, fill=0.2, width=3, pad=0) for x in F3_XS]
            self.play_at(self.cue(cue_word), LaggedStart(*[Create(r) for r in rs], lag_ratio=0.35), run_time=1.0)
            return rs

        ta = tick_seq(fa, "NYU")
        tb = tick_seq(fb, "SUN")
        ya = fa.get_bottom()[1] - 0.2
        arr_a = Arrow([fa.pt(450, 0)[0], ya, 0], [fa.pt(2050, 0)[0], ya, 0], buff=0, color=GOOD, stroke_width=5)
        arr_b = Arrow([fb.pt(450, 0)[0], ya, 0], [fb.pt(2050, 0)[0], ya, 0], buff=0, color=GOOD, stroke_width=5)
        t_up = T("越负 → 平均、最差准确率越高", size=21, color=GOOD).next_to(arr_a, DOWN, 0.1).set_x(0)
        self.play_at(self.cue("越"), *[FadeOut(r) for r in ta + tb], FadeOut(leg), run_time=0.3)
        self.play(GrowArrow(arr_a), GrowArrow(arr_b), FadeIn(t_up), run_time=0.6)

        # NYU: MSP median is not above Static
        b = BOX3["fig3a"]["boxes"]
        m_s, m_m = b[0]["lines"][2], b[1]["lines"][2]
        hs = Line(fa.pt(F3_XS[0] - 110, m_s), fa.pt(F3_XS[1] + 110, m_s), color=WARN, stroke_width=4)
        hm = Line(fa.pt(F3_XS[1] - 105, m_m), fa.pt(F3_XS[1] + 105, m_m), color=ACCENT, stroke_width=6)
        note = tag("NYU：MSP 中位数（≈0.44）略低于静态", color=WARN, size=20).next_to(fa, DOWN, 0.5).align_to(fa, LEFT)
        self.play_at(self.cue("但"), FadeOut(t_up), run_time=0.3)
        self.play_at(self.cue("第二个"), Create(hs), Create(hm), FadeIn(note), run_time=0.7)
        self.play(Indicate(hm, color=ACCENT, scale_factor=1.0), run_time=0.6)
        warn = tag("相关 ≠ 因果；每张图只有 4 个点", color=ACCENT, size=22).next_to(fb, DOWN, 0.5).align_to(fb, RIGHT)
        self.play_at(self.cue("只是"), FadeIn(warn, shift=UP * 0.1), run_time=0.5)


class S5_3(Shot):
    sid = "5-3"

    def body(self):
        tab = Crop(9, (52, 205, 298, 331), width=6.6, scale_px=2.0).move_to([-3.25, 0.75, 0])
        src = self.source("出处：Table 3（UPMC FOOD101）")
        self.play_at(self.cue("Table"), FadeIn(tab, shift=UP * 0.15), FadeIn(src), run_time=0.6)
        pos = tab.rect((140, 263, 262, 312), color=ACCENT, fill=0.12, width=2.5, pad=1.5)
        self.play_at(self.cue("正"), Create(pos), run_time=0.5)

        need = VGroup(T("式 6 要求", size=22, color=MUTED), M(r"r\big(w,\ \ell\big)\le 0", size=38, color=ORANGE)).arrange(DOWN, buff=0.12)
        got = VGroup(T("Table 3 报告", size=22, color=MUTED), M(r"r>0", size=38, color=ACCENT)).arrange(DOWN, buff=0.12)
        q = TB("?", size=54, color=WARN)
        cmp_ = VGroup(need, q, got).arrange(RIGHT, buff=0.6).move_to([3.7, 2.1, 0])
        self.play_at(self.cue("与"), FadeIn(need), FadeIn(got), run_time=0.5)
        self.play_at(self.cue("相反"), FadeIn(q, scale=1.5), run_time=0.4)

        ours = tab.rect((90, 316, 262, 328), color=WARN, fill=0.1, width=3, pad=1.0)
        self.play_at(self.cue("完整"), FadeOut(pos), Create(ours), run_time=0.5)
        cell = tab.rect(find_word(9, "0.735"), color=WARN, fill=0.25, width=4, pad=1.5)
        self.play_at(self.cue("0.735"), Create(cell), run_time=0.5)
        a0, a1 = find_word(9, "(a"), find_word(9, "estimation).")
        cap1 = tab.rect((a0[0], a0[1], 292, a0[3]), color=ACCENT, fill=0.2, width=2.5, pad=0.8)
        cap2 = tab.rect((54, a1[1], a1[2], a1[3]), color=ACCENT, fill=0.2, width=2.5, pad=0.8)
        quote = T("表注：a higher |r| indicates a better uncertainty estimation", size=18, color=ACCENT, slant=ITALIC)
        quote.next_to(tab, DOWN, 0.2)
        self.play_at(self.cue("表注"), Create(cap1), Create(cap2), FadeIn(quote), run_time=0.6)

        h1 = VGroup(T("推测 ①：算的是不确定度与损失的相关", size=21),
                    M(r"r(w,\ell) = -\,r(u,\ell)\quad(\alpha<0,\ \text{见 4-3})", size=30))
        h1.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        h2 = VGroup(T("推测 ②：报的是绝对值", size=21), M(r"|r|", size=34)).arrange(RIGHT, buff=0.3)
        c1 = card(h1, pad=0.22)
        c2 = card(h2, pad=0.22)
        VGroup(c1, c2).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([3.75, -0.15, 0])
        self.play_at(self.cue("可能"), FadeIn(c1, shift=LEFT * 0.15), run_time=0.6)
        self.play_at(self.cue("可能", k=1), FadeIn(c2, shift=LEFT * 0.15), run_time=0.6)
        warn = tag("论文未说明，属推测", color=WARN, size=22).next_to(VGroup(c1, c2), DOWN, 0.3)
        self.play_at(self.cue("论文"), FadeIn(warn, scale=0.9), run_time=0.5)


# Table 1 block y-ranges (pt) and Ours rows
T1_BLOCKS = {"NYU": (172, 276), "SUN": (296, 400), "FOOD": (424, 540), "MVSA": (575, 681)}


class S5_4(Shot):
    sid = "5-4"

    def body(self):
        t1 = Crop(8, (113, 120.5, 484, 682), height=5.8, scale_px=2.6, pad=0.1).move_to([-4.6, 0.02, 0])
        src = self.source("出处：Table 1、附录 Table 5、Table 2")
        cols = t1.rect((340, 121, 482, 150), color=ACCENT, fill=0.15, width=2.5, pad=0.5)
        self.play_at(self.cue("Table"), FadeIn(t1, shift=UP * 0.15), FadeIn(src), run_time=0.6)
        self.play_at(self.cue("噪声"), Create(cols), run_time=0.5)
        ours_rects = []
        for k, (y0, y1) in T1_BLOCKS.items():
            o = find_word(8, "Ours", region=(200, y0, 260, y1))
            ours_rects.append(t1.rect((340, o[1], 482, o[3]), color=BASELINE, fill=0.3, width=3, pad=1.2))
        title = TB("ε = 5、10：QMF 平均、最差准确率 16 格全部第一", size=23, color=BASELINE).move_to([2.35, 2.75, 0])
        self.play_at(self.cue("QMF"), LaggedStart(*[Create(r) for r in ours_rects], lag_ratio=0.4), FadeIn(title), run_time=1.6)
        self.play(*[Indicate(r, color=BASELINE, scale_factor=1.05) for r in ours_rects], run_time=0.6)

        # lead smaller than one std
        o_nyu = find_word(8, "61.62", region=(340, 172, 370, 276))
        t_nyu = find_word(8, "61.04", region=(340, 172, 370, 276))
        r1 = t1.rect(o_nyu, color=WARN, fill=0.0, width=3, pad=1.5)
        r2 = t1.rect(t_nyu, color=WARN, fill=0.0, width=3, pad=1.5)
        mt = MobjectTable(
            [[T("61.04", size=24), T("± 1.66", size=24, color=MUTED)], [T("61.62", size=24, color=ACCENT), T("± 1.84", size=24, color=WARN)]],
            row_labels=[T("TMC", size=24), T("Ours", size=24, color=ACCENT)],
            col_labels=[T("平均", size=20, color=MUTED), T("标准差", size=20, color=MUTED)],
            include_outer_lines=False, line_config={"stroke_width": 1, "color": FAINT}, h_buff=0.45, v_buff=0.22)
        mt_t = T("NYU · ε = 5（均值：Table 1；标准差：附录 Table 5）", size=18, color=MUTED)
        lead = VGroup(T("领先", size=22), TB("0.58", size=26, color=ACCENT), T("<", size=24), T("标准差", size=22),
                      TB("1.84", size=26, color=WARN)).arrange(RIGHT, buff=0.12)
        blk = VGroup(mt_t, mt, lead).arrange(DOWN, buff=0.18).move_to([2.35, 1.0, 0])
        self.play_at(self.cue("NYU"), *[r.animate.set_opacity(0.25) for r in ours_rects], Create(r1), Create(r2), run_time=0.5)
        self.play(FadeIn(mt_t), FadeIn(mt), run_time=0.5)
        self.play_at(self.cue("0.58"), FadeIn(lead[:2]), run_time=0.4)
        self.play_at(self.cue("1.84"), FadeIn(lead[2:]), run_time=0.5)

        # ablation
        t2 = Crop(9, (128, 92, 468, 178), width=6.4, scale_px=2.0).move_to([2.35, 0.85, 0])
        t2_t = T("Table 2 · 消融（NYU）", size=18, color=MUTED).next_to(t2, UP, 0.08).align_to(t2, LEFT)
        self.play_at(self.cue("Table", k=2), FadeOut(blk), FadeOut(r1), FadeOut(r2), FadeIn(t2, shift=UP * 0.15),
                     FadeIn(t2_t), run_time=0.6)
        avg_x = [(193, 217), (263, 287), (333, 357), (404, 427)]
        rows_y = [(124, 133), (136, 145), (148, 157), (165, 175)]
        single = VGroup(*[t2.rect((x0, rows_y[r][0], x1, rows_y[r][1]), color=TEAL, fill=0.2, width=2, pad=1)
                          for r in (1, 2) for x0, x1 in avg_x])
        base = VGroup(*[t2.rect((x0, rows_y[0][0], x1, rows_y[0][1]), color=MUTED, fill=0.15, width=2, pad=1) for x0, x1 in avg_x])
        both = VGroup(*[t2.rect((x0, rows_y[3][0], x1, rows_y[3][1]), color=GOOD, fill=0.3, width=3, pad=1) for x0, x1 in avg_x])
        lab_a = T("单用任一组件 > 静态（平均）", size=20, color=TEAL)
        lab_b = T("合用：每个噪声级别平均最高", size=20, color=GOOD)
        VGroup(lab_a, lab_b).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(t2, DOWN, 0.2).align_to(t2, LEFT)
        self.play_at(self.cue("单"), FadeIn(base), FadeIn(single), FadeIn(lab_a), run_time=0.6)
        self.play_at(self.cue("合用"), FadeIn(both), FadeIn(lab_b), run_time=0.6)
        w1 = t2.rect(find_word(9, "69.11"), color=ORANGE, fill=0.0, width=3, pad=1.2)
        w2 = t2.rect(find_word(9, "51.53"), color=ORANGE, fill=0.0, width=3, pad=1.2)
        lab_c = T("最差准确率：非合用组合也有最佳（69.11、51.53）", size=18, color=ORANGE).next_to(lab_b, DOWN, 0.1).align_to(lab_b, LEFT)
        self.play(Create(w1), Create(w2), FadeIn(lab_c), run_time=0.6)

        # clean data: not always first
        o0 = find_word(8, "70.09", region=(270, 172, 300, 276))
        k0 = find_word(8, "71.06", region=(270, 172, 300, 276))
        c0 = t1.rect((270, 121, 336, 150), color=WARN, fill=0.12, width=2.5, pad=0.5)
        q0 = t1.rect(o0, color=WARN, fill=0.25, width=3, pad=1.5)
        q1 = t1.rect(k0, color=GOOD, fill=0.25, width=3, pad=1.5)
        clean = VGroup(T("干净数据（ε = 0）不总第一：", size=21), T("NYU  Ours 70.09 < TMC 71.06", size=22, color=WARN))
        clean.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        cc = card(clean, pad=0.18).move_to([2.35, -2.25, 0])
        self.play_at(self.cue("干净"), FadeOut(cols), *[FadeOut(r) for r in ours_rects], Create(c0), run_time=0.5)
        self.play_at(self.cue("70.09"), Create(q0), FadeIn(cc), run_time=0.5)
        self.play_at(self.cue("71.06"), Create(q1), run_time=0.5)


class S5_5(Shot):
    sid = "5-5"

    def body(self):
        def column(title, col, x):
            h = TB(title, size=28, color=col)
            line = Line(LEFT * 3.0, RIGHT * 3.0, color=col, stroke_width=2).next_to(h, DOWN, 0.15)
            g = VGroup(h, line).move_to([x, 2.55, 0])
            return g

        left = column("论文自述（第 6 节）", TEAL, -3.45)
        right = column("我们补充", ACCENT, 3.45)
        self.play_at(self.cue("局限"), FadeIn(left), FadeIn(right), run_time=0.6)

        def item(num, lines, col, anchor):
            n = TB(num, size=24, color=col)
            body = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            g = VGroup(n, body).arrange(RIGHT, aligned_edge=UP, buff=0.18)
            return g.next_to(anchor, DOWN, 0.5).align_to(anchor, LEFT)

        l1 = item("①", [T("NYU、SUN 上不确定度与损失", size=25), T("只有温和相关（mild Pearson's r）", size=25)], TEAL, left)
        l2 = item("②", [T("理论依赖假设 1", size=25), T("能量分数出自分布外检测（OOD）", size=22, color=MUTED),
                        T("= 识别陌生输入", size=22, color=MUTED), T("已有研究：某些场景下不可学", size=25),
                        T("（Fang et al., 2022）→ 假设未必成立", size=22, color=MUTED)], TEAL, l1)
        self.play_at(self.cue("论文"), FadeIn(l1[0]), run_time=0.3)
        self.play_at(self.cue("RGB"), FadeIn(l1[1], shift=RIGHT * 0.1), run_time=0.5)
        self.play_at(self.cue("理论"), FadeIn(l2[0]), FadeIn(l2[1][0], shift=RIGHT * 0.1), run_time=0.5)
        self.play_at(self.cue("能"), FadeIn(l2[1][1]), run_time=0.4)
        self.play_at(self.cue("即"), FadeIn(l2[1][2]), run_time=0.4)
        self.play_at(self.cue("已"), FadeIn(l2[1][3]), FadeIn(l2[1][4]), run_time=0.5)

        r1 = item("①", [T("理论只管决策级晚期融合", size=25), T("和二分类", size=25)], ACCENT, right)
        r2 = item("②", [T("实验只有两个模态（M = 2）", size=25)], ACCENT, r1)
        r3 = item("③", [T("没报告式 5 是否满足", size=25), M(r"\mathbb{E}(w_{\text{dynamic}}) = w_{\text{static}}\ ?", size=30)],
                  ACCENT, r2)
        self.play_at(self.cue("我们"), Indicate(right[0], color=ACCENT, scale_factor=1.06), run_time=0.6)
        self.play_at(self.cue("理论", k=1), FadeIn(r1, shift=LEFT * 0.1), run_time=0.5)
        self.play_at(self.cue("实验"), FadeIn(r2, shift=LEFT * 0.1), run_time=0.5)
        self.play_at(self.cue("没"), FadeIn(r3, shift=LEFT * 0.1), run_time=0.5)


class S5_6(Shot):
    sid = "5-6"

    def body(self):
        f = Crop("fig2.png", (0, 820, 4960, 1380), width=10.5, scale_px=2.0).move_to([0, 2.1, 0])
        veil = f.veil(keep_boxes=[(2960, 1000, 4040, 1370)], opacity=0.72, color=WHITE)
        src = self.source("Figure 2（左）上界式")
        self.play_at(self.cue("收尾"), FadeIn(f), FadeIn(src), run_time=0.5)
        self.play(FadeIn(veil), run_time=0.5)
        cov = f.rect((2960, 1000, 4040, 1370), color=ORANGE, fill=0.0, width=4, pad=10)
        self.play(Create(cov), run_time=0.4)

        def summary(num, lines, col):
            body = VGroup(*[T(l, size=24) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            n = TB(num, size=34, color=col)
            g = VGroup(n, body).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            box = RoundedRectangle(corner_radius=0.18, width=4.2, height=2.9, fill_color=PANEL, fill_opacity=1,
                                   stroke_color=col, stroke_width=2.5)
            g.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.3)
            return VGroup(box, g)

        c1 = summary("1", ["固定权重", "不会少听变脏的一路"], BASELINE)
        c2 = summary("2", ["动态融合赢在", "权重与损失的负协方差", "（只在上界意义上）"], ORANGE)
        c3 = summary("3", ["QMF：能量估计各路", "多拿不准，再用历史", "损失排序把它练准"], ACCENT)
        row = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.3).move_to([0, -0.95, 0])
        for c, cue in ((c1, "固定"), (c2, "动态"), (c3, "QMF")):
            self.play_at(self.cue(cue), FadeIn(c, shift=UP * 0.2), run_time=0.5)
            # rotate-in feel
        self.play(Indicate(cov, color=ORANGE, scale_factor=1.04), run_time=0.8)
