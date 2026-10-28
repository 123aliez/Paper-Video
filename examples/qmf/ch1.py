from common import *

FIG1 = json.loads((ASSETS / "fig1_bars.json").read_text())


def node(text, w=1.6, h=0.6, color=BASELINE, size=22, fill=0.15):
    box = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=2.5,
                           fill_color=color, fill_opacity=fill)
    return VGroup(box, T(text, size=size).move_to(box))


def text_doc(lines, w=1.9, h=1.45, size=17):
    box = RoundedRectangle(corner_radius=0.1, width=w, height=h, fill_color="#F4F1EA", fill_opacity=1,
                           stroke_width=0)
    t = VGroup(*[T(l, size=size, color="#2B2B2B") for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    t.move_to(box)
    return VGroup(box, t)


def sunset_pic(w=1.9, h=1.45):
    sky = Rectangle(width=w, height=h * 0.62, stroke_width=0).set_fill(["#FFB347", "#FF6F61"], 1)
    sky.set_sheen_direction(DOWN)
    sea = Rectangle(width=w, height=h * 0.38, stroke_width=0, fill_color="#2E5E8C", fill_opacity=1)
    VGroup(sky, sea).arrange(DOWN, buff=0)
    sun = Circle(radius=h * 0.16, stroke_width=0, fill_color="#FFE08A", fill_opacity=1)
    sun.move_to(sky.get_bottom() + UP * h * 0.12)
    sun_ref = Rectangle(width=h * 0.25, height=0.04, stroke_width=0, fill_color="#FFE08A",
                        fill_opacity=0.8).move_to(sea.get_top() + DOWN * 0.12)
    g = VGroup(sky, sea, sun, sun_ref)
    frame = RoundedRectangle(corner_radius=0.08, width=w, height=h, stroke_color=WHITE, stroke_width=2)
    return VGroup(g, frame.move_to(g))


def dish_pic(w=1.9, h=1.45):
    bg = Rectangle(width=w, height=h, stroke_width=0, fill_color="#5A3E2B", fill_opacity=1)
    plate = Circle(radius=h * 0.4, stroke_width=0, fill_color="#F7F7F2", fill_opacity=1)
    rim = Circle(radius=h * 0.3, stroke_color="#DDDDD5", stroke_width=2)
    blobs = VGroup()
    rng = np.random.default_rng(3)
    for i in range(9):
        c = "#E8442E" if i % 2 else "#F6C945"
        r = 0.09 + 0.05 * rng.random()
        blobs.add(Circle(radius=r, stroke_width=0, fill_color=c, fill_opacity=1)
                  .move_to([0.32 * (rng.random() - 0.5) * h * 2, 0.28 * (rng.random() - 0.5) * h * 2, 0]))
    for i in range(5):
        blobs.add(Dot(radius=0.025, color="#3FA34D").move_to([(rng.random() - 0.5) * h * 0.6,
                                                             (rng.random() - 0.5) * h * 0.5, 0]))
    g = VGroup(bg, plate, rim, blobs)
    frame = RoundedRectangle(corner_radius=0.08, width=w, height=h, stroke_color=WHITE, stroke_width=2)
    return VGroup(g, frame.move_to(bg))


def framed_image(path, w):
    im = ImageMobject(str(ASSETS / path)).set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])
    im.width = w
    fr = RoundedRectangle(corner_radius=0.06, width=im.width, height=im.height, stroke_color=WHITE,
                          stroke_width=2).move_to(im)
    return Group(im, fr)


class S1_1(Shot):
    sid = "1-1"
    skip_intro = True

    def body(self):
        # chapter 1 follows the title card, so just bring the corner tag in
        self.play(FadeIn(self.tagm), run_time=0.4)
        top_y = 1.75
        # column 1: robot room
        rgb = framed_image("room_rgb.png", 2.15)
        dep = framed_image("room_depth.png", 2.15)
        col1 = Group(rgb, dep).arrange(RIGHT, buff=0.2)
        col1.move_to([-4.45, top_y, 0])
        l_rgb = T("RGB 彩色照片", size=20).next_to(rgb, DOWN, 0.15)
        l_dep = T("深度图（近亮远暗）", size=20).next_to(dep, DOWN, 0.15)
        head1 = TB("机器人认房间", size=24, color=ACCENT).next_to(col1, UP, 0.22)
        # column 2: social post
        pic2 = sunset_pic()
        doc2 = text_doc(["终于放假了，", "阳光正好！"])
        col2 = VGroup(pic2, doc2).arrange(RIGHT, buff=0.2).move_to([0.55, top_y, 0])
        head2 = TB("帖子情绪", size=24, color=ACCENT).next_to(col2, UP, 0.22)
        # column 3: dish
        pic3 = dish_pic()
        doc3 = text_doc(["番茄炒蛋：", "番茄、鸡蛋、", "葱花"])
        col3 = VGroup(pic3, doc3).arrange(RIGHT, buff=0.2).move_to([4.75, top_y, 0])
        head3 = TB("菜品类别", size=24, color=ACCENT).next_to(col3, UP, 0.22)
        l_img2 = T("图片", size=20).next_to(pic2, DOWN, 0.15)
        l_txt2 = T("文字", size=20).next_to(doc2, DOWN, 0.15)
        l_img3 = T("图片", size=20).next_to(pic3, DOWN, 0.15)
        l_txt3 = T("文字", size=20).next_to(doc3, DOWN, 0.15)
        heads = [head1, head2, head3]
        VGroup(*heads).align_to(head1, UP)

        self.play_at(self.cue("机器人"), FadeIn(head1, shift=DOWN * 0.1), run_time=0.4)
        self.play_at(self.cue("彩色照片"), FadeIn(rgb, shift=UP * 0.15), FadeIn(l_rgb), run_time=0.6)
        self.play_at(self.cue("深度图"), FadeIn(dep, shift=UP * 0.15), FadeIn(l_dep), run_time=0.6)
        # pixel-distance callout on the depth map
        px = Dot(dep[0].get_center() + DOWN * 0.45 + RIGHT * 0.1, radius=0.045, color=ACCENT)
        ring = Circle(radius=0.13, color=ACCENT, stroke_width=2.5).move_to(px)
        note = T("每个像素 = 到镜头的距离", size=19, color=ACCENT)
        note.next_to(l_dep, DOWN, 0.14).align_to(dep, RIGHT)
        self.play_at(self.cue("每个"), FadeIn(px, scale=2), Create(ring), FadeIn(note), run_time=0.6)

        self.play_at(self.cue("判断帖子情绪"), FadeIn(head2), FadeIn(col2, shift=UP * 0.15), run_time=0.6)
        self.play_at(self.cue("菜品类别"), FadeIn(head3), FadeIn(col3, shift=UP * 0.15), run_time=0.6)
        self.play_at(self.cue("图片"), FadeIn(l_img2), FadeIn(l_img3), run_time=0.4)
        self.play_at(self.cue("文字"), FadeIn(l_txt2), FadeIn(l_txt3), run_time=0.4)

        # arrows into fusion boxes, then outputs
        fuse_y, out_y = -0.95, -2.2
        boxes, arrows, outs = [], [], []
        specs = [(col1, [rgb, dep], "卧室", -4.45), (col2, [pic2, doc2], "正面情绪", 0.55),
                 (col3, [pic3, doc3], "菜品类别", 4.75)]
        for col, items, out, x in specs:
            fb = node("融合", w=1.5, h=0.62, color=ACCENT, size=24).move_to([x, fuse_y, 0])
            boxes.append(fb)
            for it in items:
                start = np.array([it.get_center()[0], 0.12, 0])
                arrows.append(Arrow(start, fb.get_top(), buff=0.05, stroke_width=3, color=MUTED,
                                    max_tip_length_to_length_ratio=0.18))
            o = node(out, w=1.9, h=0.55, color=GOOD, size=22).move_to([x, out_y, 0])
            arrows.append(Arrow(fb.get_bottom(), o.get_top(), buff=0.05, stroke_width=3, color=MUTED,
                                max_tip_length_to_length_ratio=0.25))
            outs.append(o)
        self.play_at(self.cue("几路信息"), LaggedStart(*[GrowArrow(a) for i, a in enumerate(arrows) if i % 3 != 2],
                                                      lag_ratio=0.08), run_time=0.9)
        self.play(*[FadeIn(b, scale=0.9) for b in boxes], run_time=0.5)
        mm = T("多模态融合", size=26, color=ACCENT, weight=BOLD)
        self.play_at(self.cue("多模态融合"), *[Indicate(b, color=ACCENT, scale_factor=1.08) for b in boxes],
                     run_time=0.6)
        self.play(*[GrowArrow(a) for i, a in enumerate(arrows) if i % 3 == 2],
                  *[FadeIn(o, shift=DOWN * 0.1) for o in outs], run_time=0.6)

        # the question
        veil = Rectangle(width=config.frame_width, height=config.frame_height, stroke_width=0,
                         fill_color=BG, fill_opacity=0.82)
        q = TB("多一路信息，总不会更差？", size=60)
        self.play_at(self.cue("多一路信息"), FadeIn(veil), Write(q), run_time=0.9)


def stacked_table1(rows_y0, rows_y1, width=7.3, x0=113, x1=484, head=(120.5, 151.5)):
    """Table 1 header + one dataset block on a single white card."""
    hdr = Crop(8, (x0, head[0], x1, head[1]), width=width, pad=0, radius=0)
    blk = Crop(8, (x0, rows_y0, x1, rows_y1), width=width, pad=0, radius=0)
    Group(hdr, blk).arrange(DOWN, buff=0.05)
    sep = Line(blk.get_corner(UL), blk.get_corner(UR), color="#888888", stroke_width=1).shift(UP * 0.025)
    bg = RoundedRectangle(corner_radius=0.1, width=width + 0.25, height=hdr.height + blk.height + 0.3,
                          fill_color=WHITE, fill_opacity=1, stroke_width=0).move_to(Group(hdr, blk))
    return Group(bg, hdr, blk, sep), hdr, blk


def t1_cell(text, block):
    """Locate a Table-1 number inside a dataset block (pt y-range)."""
    return find_word(8, text, region=(250, block[0], 490, block[1]))


MVSA = (575, 681)


class S1_2(Shot):
    sid = "1-2"

    def body(self):
        tab, hdr, blk = stacked_table1(*MVSA, width=7.7)
        tab.move_to([-2.75, 0.45, 0])
        title = T("Table 1 · MVSA（图文情感）", size=24, color=MUTED).next_to(tab, UP, 0.2).align_to(tab, LEFT)
        src = self.source("出处：Table 1，MVSA，平均准确率（%）")
        self.play_at(self.cue("Table"), FadeIn(tab, shift=UP * 0.15), FadeIn(title), FadeIn(src), run_time=0.7)

        # bar chart on the right
        ax = Axes(x_range=[0, 2.4, 1], y_range=[40, 80, 10], x_length=4.5, y_length=3.7,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  y_axis_config={"include_numbers": True, "font_size": 20, "include_ticks": True},
                  tips=False)
        ax.move_to([4.15, -0.05, 0])
        grid = VGroup(*[DashedLine(ax.c2p(0, v), ax.c2p(2.4, v), color=FAINT, stroke_width=1)
                        for v in (50, 60, 70, 80)])
        g_lab = VGroup(T("干净 ε = 0", size=20, color=MUTED).move_to(ax.c2p(0.55, 40) + DOWN * 0.3),
                       T("噪声 ε = 5", size=20, color=MUTED).move_to(ax.c2p(1.65, 40) + DOWN * 0.3))
        legend = VGroup(
            VGroup(Square(0.22, fill_color=TEAL, fill_opacity=1, stroke_width=0), T("BERT（只用文本）", size=19)).arrange(RIGHT, buff=0.12),
            VGroup(Square(0.22, fill_color=BASELINE, fill_opacity=1, stroke_width=0), T("晚期融合（固定权重）", size=19)).arrange(RIGHT, buff=0.12),
        ).arrange(RIGHT, buff=0.35).next_to(ax, UP, 0.3)

        def bar(xc, v, color):
            p0, p1 = ax.c2p(xc - 0.17, 40), ax.c2p(xc + 0.17, v)
            r = Rectangle(width=p1[0] - p0[0], height=p1[1] - p0[1], stroke_width=0, fill_color=color,
                          fill_opacity=1).move_to((p0 + p1) / 2)
            lab = T(f"{v:.2f}", size=20, color=color).next_to(r, UP, 0.06)
            return r, lab

        self.play_at(self.cue("干净"), Create(ax), FadeIn(grid), FadeIn(g_lab), FadeIn(legend), run_time=0.8)

        bert_row = find_word(8, "Bert", region=(200, MVSA[0], 260, MVSA[1]))
        lf_row = find_word(8, "Late", region=(200, MVSA[0], 260, MVSA[1]))
        row_bert = blk.rect((120, bert_row[1], 482, bert_row[3]), color=TEAL, fill=0.12, width=2, pad=0.8)
        row_lf = blk.rect((120, lf_row[1], 482, lf_row[3]), color=BASELINE, fill=0.12, width=2, pad=0.8)

        def cell(v):
            return blk.rect(t1_cell(v, MVSA), color=WARN, fill=0.0, width=3, pad=1.6)

        self.play_at(self.cue("BERT"), FadeIn(row_bert), run_time=0.4)
        b1, l1 = bar(0.37, 75.61, TEAL)
        self.play_at(self.cue("75.61"), Create(cell("75.61")), GrowFromEdge(b1, DOWN), FadeIn(l1), run_time=0.7)
        self.play_at(self.cue("晚期融合"), FadeIn(row_lf), run_time=0.4)
        b2, l2 = bar(0.73, 76.88, BASELINE)
        self.play_at(self.cue("76.88"), Create(cell("76.88")), GrowFromEdge(b2, DOWN), FadeIn(l2), run_time=0.7)
        eps5 = find_word(8, "5.0", region=(370, 120, 400, 136))
        h5 = hdr.rect((340, eps5[1], 410, eps5[3]), color=ACCENT, fill=0.15, width=2.5, pad=1.0)
        self.play_at(self.cue("噪声强度"), FadeIn(h5), run_time=0.4)
        b3, l3 = bar(1.47, 69.50, TEAL)
        self.play_at(self.cue("69.50"), Create(cell("69.50")), GrowFromEdge(b3, DOWN), FadeIn(l3), run_time=0.7)
        b4, l4 = bar(1.83, 63.46, BASELINE)
        self.play_at(self.cue("63.46"), Create(cell("63.46")), GrowFromEdge(b4, DOWN), FadeIn(l4), run_time=0.7)
        # difference
        y_top, y_bot = b3.get_top()[1], b4.get_top()[1]
        xr = b4.get_right()[0] + 0.15
        br = VGroup(Line([xr, y_top, 0], [xr + 0.12, y_top, 0]), Line([xr + 0.12, y_top, 0], [xr + 0.12, y_bot, 0]),
                    Line([xr, y_bot, 0], [xr + 0.12, y_bot, 0])).set_stroke(WARN, 3)
        d = TB("−6.04", size=26, color=WARN).next_to(br, RIGHT, 0.08)
        self.play_at(self.cue("低"), Create(br), FadeIn(d, shift=LEFT * 0.1), run_time=0.6)
        self.play(Indicate(d, color=WARN), run_time=0.6)


class S1_3(Shot):
    sid = "1-3"

    def body(self):
        imgs = [framed_image(f"room_noise_{e}.png", 2.15) for e in (0, 5, 10)]
        row = Group(*imgs).arrange(RIGHT, buff=0.2).move_to([-3.5, 1.45, 0])
        labs = VGroup(*[M(rf"\epsilon = {e}", size=30).next_to(im, DOWN, 0.12) for im, e in zip(imgs, (0, 5, 10))])
        head = TB("图像：高斯噪声", size=24, color=ACCENT).next_to(row, UP, 0.2).align_to(row, LEFT)
        formula = M(r"\tilde{x}_{\text{img}} = x_{\text{img}} + n,\qquad n \sim \mathcal{N}(0,\ \epsilon)", size=40)
        formula.next_to(labs, DOWN, 0.3)
        f_note = T("ε = 噪声的方差", size=20, color=MUTED).next_to(formula, DOWN, 0.12)
        self.play_at(self.cue("噪声"), FadeIn(head), FadeIn(imgs[0]), FadeIn(labs[0]), run_time=0.5)
        self.play_at(self.cue("图像"), FadeIn(imgs[1]), FadeIn(labs[1]), run_time=0.4)
        self.play(FadeIn(imgs[2]), FadeIn(labs[2]), run_time=0.4)
        self.play_at(self.cue("方差"), Write(formula), FadeIn(f_note), run_time=0.8)

        # text modality
        doc = text_doc(["终于放假了，阳光正好！"], w=3.9, h=0.9, size=22)
        head_t = TB("文本：blank noise（空白噪声）", size=24, color=ACCENT)
        tcol = VGroup(head_t, doc).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([3.6, 2.0, 0])
        tg1 = tag("blank noise：论文未定义", color=WARN, size=21)
        tg2 = tag("ε 对文本指什么？论文未说明", color=WARN, size=21)
        VGroup(tg1, tg2).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(doc, DOWN, 0.25).align_to(doc, LEFT)
        self.play_at(self.cue("文本"), FadeIn(tcol, shift=LEFT * 0.2), run_time=0.5)
        self.play_at(self.cue("论文"), FadeIn(tg1, scale=0.9), run_time=0.4)
        self.play_at(self.cue("强度", k=1), FadeIn(tg2, scale=0.9), run_time=0.4)

        # table note
        cap = Crop(8, (54, 75.5, 404, 86.5), width=11.6, pad=0.12)
        cap.move_to([0, -1.85, 0])
        when = find_word(8, "when", region=(150, 70, 260, 90))
        corr = find_word(8, "corrupted", region=(280, 70, 340, 90))
        hl = cap.rect((when[0], when[1], corr[2], corr[3]), color=ACCENT, fill=0.2, width=2.5, pad=1.0)
        self.play_at(self.cue("表注"), FadeIn(cap, shift=UP * 0.15), run_time=0.5)
        self.play_at(self.cue("百分之五十"), Create(hl), run_time=0.5)
        q = tag("怎么选 50%？论文未说明", color=WARN, size=22).next_to(hl, DOWN, 0.22)
        self.play_at(self.cue("怎么"), FadeIn(q, shift=UP * 0.1), run_time=0.4)


class S1_4(Shot):
    sid = "1-4"

    def body(self):
        # balance with two voters
        c = np.array([-3.3, 0.7, 0])
        post = Line(c + DOWN * 1.6, c + UP * 0.6, color=MUTED, stroke_width=5)
        base = Polygon(c + DOWN * 1.6 + LEFT * 0.6, c + DOWN * 1.6 + RIGHT * 0.6, c + DOWN * 1.25,
                       stroke_width=0, fill_color=MUTED, fill_opacity=1)
        beam = Line(c + UP * 0.6 + LEFT * 2.3, c + UP * 0.6 + RIGHT * 2.3, color=INK, stroke_width=6)
        pivot = Dot(c + UP * 0.6, radius=0.09, color=ACCENT)

        def pan(x):
            top = c + UP * 0.6 + RIGHT * x
            plate = Line(top + DOWN * 1.25 + LEFT * 0.75, top + DOWN * 1.25 + RIGHT * 0.75, stroke_width=5, color=INK)
            strings = VGroup(Line(top, plate.get_start()), Line(top, plate.get_end())).set_stroke(MUTED, 2)
            return VGroup(strings, plate)

        lp, rp = pan(-2.0), pan(2.0)
        img = framed_image("room_rgb.png", 1.2).next_to(lp[1], UP, 0.05)
        img_noisy = framed_image("room_noise_10.png", 1.2).move_to(img)
        doc = text_doc(["阳光正好！"], w=1.2, h=0.9, size=18).next_to(rp[1], UP, 0.05)
        w_l = M(r"w = 0.5", size=30, color=ACCENT).next_to(lp[1], DOWN, 0.15)
        w_r = M(r"w = 0.5", size=30, color=ACCENT).next_to(rp[1], DOWN, 0.15)
        lab_l = T("图像", size=20, color=MUTED).next_to(w_l, DOWN, 0.08)
        lab_r = T("文本", size=20, color=MUTED).next_to(w_r, DOWN, 0.08)
        scale = Group(post, base, beam, pivot, lp, rp, img, doc, w_l, w_r, lab_l, lab_r)
        self.play_at(self.cue("原因"), FadeIn(scale), run_time=0.7)
        f = M(r"f_{\text{static}}(x) = \sum_{m=1}^{M} w^m_{\text{static}}\, f^m\big(x^{(m)}\big)", size=34)
        fn = T("w 是常数，不随输入变化", size=20, color=MUTED)
        fg = VGroup(f, fn).arrange(DOWN, buff=0.12).move_to([-3.3, -2.25, 0])
        self.play_at(self.cue("固定权重"), Write(f), FadeIn(fn), run_time=0.9)
        self.play_at(self.cue("变脏"), FadeIn(img_noisy), run_time=0.8)
        self.remove(img)
        scale.remove(img)
        self.play_at(self.cue("脏的一路"), Indicate(w_l, color=WARN, scale_factor=1.3), run_time=0.8)
        same = T("权重不变，照样投票", size=20, color=WARN).next_to(lab_l, DOWN, 0.12)
        self.play_at(self.cue("照样"), FadeIn(same), run_time=0.4)

        # ConcatBert numbers
        tb = MobjectTable(
            [[T("75.61", size=24), T("69.50", size=24)],
             [T("65.59", size=24, color=WARN), T("50.70", size=24, color=WARN)]],
            row_labels=[T("BERT", size=24), T("ConcatBert", size=24, color=WARN)],
            col_labels=[M(r"\epsilon=0", size=30), M(r"\epsilon=5", size=30)],
            include_outer_lines=False, line_config={"stroke_width": 1, "color": FAINT},
            h_buff=0.5, v_buff=0.28,
        ).move_to([3.4, 1.1, 0])
        tb_title = T("Table 1 · MVSA · 平均准确率", size=20, color=MUTED).next_to(tb, UP, 0.2)
        self.play_at(self.cue("Concat"), FadeIn(tb_title), FadeIn(tb), run_time=0.6)
        diff = TB("干净时就低 10.02", size=24, color=WARN).next_to(tb, DOWN, 0.3)
        self.play_at(self.cue("干净"), Circumscribe(VGroup(tb.get_entries((2, 2)), tb.get_entries((3, 2))),
                                                   color=WARN), FadeIn(diff), run_time=0.8)

        # late fusion vs concatenation
        self.play_at(self.cue("又是"), FadeOut(scale), FadeOut(img_noisy), FadeOut(f), FadeOut(fn), FadeOut(same),
                     Group(tb_title, tb, diff).animate.scale(0.0001).move_to([3.4, 3, 0]).set_opacity(0),
                     run_time=0.5)
        left = self.late_diagram().move_to([-3.4, 0.25, 0])
        right = self.concat_diagram().move_to([3.4, 0.25, 0])
        div = DashedLine(UP * 2.6, DOWN * 2.2, color=FAINT)
        self.play(FadeIn(left, shift=UP * 0.15), FadeIn(right, shift=UP * 0.15), Create(div), run_time=0.7)
        note = T("不能全怪固定权重", size=24, color=ACCENT).move_to([3.4, -2.45, 0])
        self.play_at(self.cue("不能"), FadeIn(note), Circumscribe(right, color=ACCENT), run_time=0.8)

    def late_diagram(self):
        title = TB("加权晚期融合", size=26, color=BASELINE)
        sub = T("各路先出判断，再加权", size=20, color=MUTED)
        i1, i2 = node("图像", 1.2, 0.5, MUTED, 20), node("文本", 1.2, 0.5, MUTED, 20)
        f1, f2 = node("f¹ 判断", 1.4, 0.5, BASELINE, 20), node("f² 判断", 1.4, 0.5, BASELINE, 20)
        r1 = VGroup(i1, f1).arrange(RIGHT, buff=0.5)
        r2 = VGroup(i2, f2).arrange(RIGHT, buff=0.5)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.45)
        s = node("Σ w·f", 1.3, 0.7, ACCENT, 22).next_to(rows, RIGHT, 0.6)
        arr = VGroup(Arrow(i1.get_right(), f1.get_left(), buff=0.05), Arrow(i2.get_right(), f2.get_left(), buff=0.05),
                     Arrow(f1.get_right(), s.get_left(), buff=0.05), Arrow(f2.get_right(), s.get_left(), buff=0.05))
        arr.set_stroke(width=3).set_color(MUTED)
        body = VGroup(rows, s, arr)
        return VGroup(title, sub, body).arrange(DOWN, buff=0.25)

    def concat_diagram(self):
        title = TB("特征拼接（Concat）", size=26, color=WARN)
        sub = T("两路特征接成一条向量，再进分类器", size=20, color=MUTED)
        i1, i2 = node("图像", 1.2, 0.5, MUTED, 20), node("文本", 1.2, 0.5, MUTED, 20)
        v1 = VGroup(*[Square(0.18, fill_color=BASELINE, fill_opacity=0.9, stroke_width=1) for _ in range(4)]).arrange(RIGHT, buff=0)
        v2 = VGroup(*[Square(0.18, fill_color=TEAL, fill_opacity=0.9, stroke_width=1) for _ in range(4)]).arrange(RIGHT, buff=0)
        r1 = VGroup(i1, v1).arrange(RIGHT, buff=0.45)
        r2 = VGroup(i2, v2).arrange(RIGHT, buff=0.45)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        cat = VGroup(v1.copy(), v2.copy()).arrange(RIGHT, buff=0).next_to(rows, RIGHT, 0.5)
        clf = node("分类器", 1.2, 0.6, WARN, 20).next_to(cat, DOWN, 0.35)
        arr = VGroup(Arrow(i1.get_right(), v1.get_left(), buff=0.05), Arrow(i2.get_right(), v2.get_left(), buff=0.05),
                     Arrow(v1.get_right(), cat.get_left() + UP * 0.05, buff=0.05),
                     Arrow(v2.get_right(), cat.get_left() + DOWN * 0.05, buff=0.05),
                     Arrow(cat.get_bottom(), clf.get_top(), buff=0.05))
        arr.set_stroke(width=3).set_color(MUTED)
        body = VGroup(rows, cat, clf, arr)
        return VGroup(title, sub, body).arrange(DOWN, buff=0.25)


class S1_5(Shot):
    sid = "1-5"

    def body(self):
        W, H, zy = FIG1["W"], FIG1["H"], FIG1["zero_y"]
        fig = Crop("fig1.png", (0, 0, W, H), width=13.2, scale_px=2.2, pad=0.1)
        fig.move_to([0, 0.75, 0])
        self.play_at(self.cue("Figure"), FadeIn(fig, shift=UP * 0.15), run_time=0.6)
        src = self.source("出处：Figure 1")
        zero = Line(fig.pt(470, zy), fig.pt(5020, zy), color=BLACK, stroke_width=4)
        note = T("柱高 = 方法平均准确率 − 最好单模态平均准确率（可用 Table 1 复算）", size=20, color=MUTED)
        note.next_to(fig, DOWN, 0.25)
        self.play_at(self.cue("比最好"), Create(zero), FadeIn(note), FadeIn(src), run_time=0.7)
        zl = T("零线", size=18, color=WARN).next_to(fig.pt(5020, zy), RIGHT, 0.12)
        self.play(FadeIn(zl), run_time=0.3)

        bars = FIG1["bars"]

        def box(b, color, width=3):
            return fig.rect((b["x0"], min(b["y0"], zy), b["x1"], max(b["y1"], zy)), color=color, fill=0.0,
                            width=width, pad=6)

        ours = [box(b, ACCENT, 3) for b in bars if b["m"] == "ours"]
        self.play_at(self.cue("粉色"), LaggedStart(*[Create(o) for o in ours], lag_ratio=0.15), run_time=1.6)
        above = tag("QMF 始终在零线以上", color=ACCENT, size=20).next_to(fig, UP, 0.12).align_to(fig, RIGHT)
        self.play_at(self.cue("始终"), FadeIn(above), run_time=0.4)

        # zoom into the image-text half to show the negative bars
        stage = Group(fig, zero, zl, *ours)
        P = fig.pt(3950, 600)
        V = LEFT * 0.4 + DOWN * 0.15
        self.play_at(self.cue("以上"), FadeOut(above), FadeOut(note),
                     stage.animate.scale(1.85, about_point=P).shift(V), run_time=0.6)
        cmap = {"late": (ORANGE, "晚期融合"), "concat": (WARN, "拼接融合"), "tmc": (PURPLE, "TMC")}
        neg = [b for b in bars if b["y0"] >= zy and b["m"] in cmap]
        legend = VGroup()
        key_cues = {"late": "晚期融合", "concat": "拼接融合", "tmc": "TMC"}
        groups = {}
        for m in ("late", "concat", "tmc"):
            col, name = cmap[m]
            rs = [box(b, col, 4) for b in neg if b["m"] == m]
            groups[m] = rs
            item = VGroup(Square(0.22, stroke_color=col, stroke_width=4), T(f"{name} · {len(rs)} 处跌破", size=20, color=col)).arrange(RIGHT, buff=0.12)
            legend.add(item)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        lg_card = card(legend, pad=0.18).to_corner(UL, buff=0.5).shift(DOWN * 0.45)
        self.add(lg_card[0].set_opacity(0))
        for i, m in enumerate(("late", "concat", "tmc")):
            anims = [Create(r) for r in groups[m]] + [FadeIn(legend[i])]
            if i == 0:
                anims.append(lg_card[0].animate.set_opacity(1))
            self.play_at(self.cue(key_cues[m]), *anims, run_time=0.6)
            self.play(*[Indicate(r, color=cmap[m][0], scale_factor=1.15) for r in groups[m]], run_time=0.4)
        self.play_at(self.cue("跌"), *[r.animate.set_fill(cmap[m][0], 0.25) for m in groups for r in groups[m]],
                     run_time=0.5)

        # zoom back out, frame the RGB-D half
        all_neg = [r for m in groups for r in groups[m]]
        stage2 = Group(stage, *all_neg)
        self.play_at(self.cue("但"), FadeOut(lg_card), FadeOut(legend),
                     stage2.animate.shift(-V).scale(1 / 1.85, about_point=P), run_time=0.7)
        self.at(self.cue("RGB"))
        rgbd = fig.rect((480, 300, 2770, 1140), color=GOOD, fill=0.06, width=4, pad=0)
        rg_t = tag("RGB-D：没有方法输给单模态", color=GOOD, size=20).next_to(fig, DOWN, 0.15).align_to(rgbd, LEFT)
        self.play(Create(rgbd), FadeIn(rg_t), run_time=0.7)

        # MVSA eps=10: late fusion beats BERT again
        lf10 = [b for b in bars if b["g"] == 11 and b["m"] == "late"][0]
        r10 = box(lf10, GOOD, 4)
        cmp_ = VGroup(
            T("MVSA · ε = 10（Table 1）", size=21, color=MUTED),
            VGroup(T("晚期融合 55.16", size=26, color=GOOD), T(">", size=26), T("BERT 47.41", size=26, color=TEAL)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, buff=0.12)
        cc = card(cmp_, pad=0.2).move_to([3.6, -2.1, 0])
        self.play_at(self.cue("MVSA"), Create(r10), run_time=0.5)
        self.play_at(self.cue("反超") - 0.6, FadeIn(cc, shift=UP * 0.15), run_time=0.6)
