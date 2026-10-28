# 阶段 3–5：从脚本到成片

## 目录

1. 技术栈与目录结构
2. 环境与项目初始化
3. 配音与时长校准
4. 论文素材
5. 写镜头（Shot API、布局、同步）
6. 预览—渲染—合成—质检循环
7. 输出：成片、不烧字幕版、4K
8. 踩过的坑

## 1. 技术栈与目录结构

| 环节 | 工具 |
|---|---|
| 动画 | Manim Community（Cairo / Pango 渲染），1920×1080、30 fps |
| 中文与公式 | Noto Sans CJK SC；MathTex 用 xelatex + xeCJK 模板（common.py 已设为默认） |
| 配音 | edge-tts（微软神经网络语音），WordBoundary 给出逐词时间戳 |
| 论文素材 | poppler：`pdftotext -bbox` 取词坐标、`pdftoppm -r 400` 渲染页面、`pdfimages` 抽原图 |
| 图像处理 | NumPy + Pillow（裁图、遮罩、按颜色定位图中元素） |
| 合成 | ffmpeg：concat 拼接、loudnorm 响度归一（−16 LUFS）、libass 烧录字幕、libx264 |
| Python 环境 | uv 建的 `.venv`（Python 3.12） |

```
<工作目录>/
├── paper.pdf
├── research.md                         阶段 1 产出
├── <短名> 论文讲解视频脚本（约 N 分钟）.md   阶段 2 产出
├── <output>.mp4 / .srt                 成片与字幕
└── production/
    ├── video.json      项目配置（标题、作者、配音、输出名）
    ├── shots.json      由脚本导出的口播
    ├── common.py       配色、文字、计时、Shot 基类、Crop
    ├── extras.py       片头 Intro / 片尾 Outro
    ├── ch1.py … chN.py 每章一个模块，每个镜头一个场景类 S<章>_<序号>
    ├── make_assets.py  （可选）程序生成的插画
    ├── tts.py  render.sh  preview.sh  assemble.py  qa_frames.py  pdf_assets.py  manim.cfg
    ├── assets/  words.json  pages/p<n>.png  figs/  text/p<n>.txt  crops/
    ├── audio/  timing/  render/  build/
```

## 2. 环境与项目初始化

```bash
SKILL=~/.claude/skills/paper-video        # 本技能所在目录
bash $SKILL/scripts/setup_env.sh <工作目录>/production    # 缺的系统包用 apt 装（需要 sudo），再建 venv
python3 $SKILL/scripts/init_project.py <工作目录>          # 复制模板，不覆盖已有文件
python3 $SKILL/scripts/script_tool.py shots "<脚本.md>" <工作目录>/production/shots.json
```

apt 安装 TeX Live 要几分钟，放后台跑（`run_in_background`），同时做别的。没有 sudo 时把缺的包列给用户。

然后填 `production/video.json`：

| 字段 | 含义 |
|---|---|
| `output` | 成片文件名（不含扩展名），如 `QMF_论文讲解` |
| `kicker` / `title_zh` / `title_en` / `authors` / `venue` | 片头卡内容 |
| `outro` / `outro_note` | 片尾卡：论文与代码出处、核实说明 |
| `voice` / `rate` | 配音音色与语速 |
| `tts_replace` | 只改读音、不改字幕的替换表，如 `"FOOD101": "FOOD 一零一"`、`"RGB-D": "RGB D"` |
| `quality` | 渲染文件夹名：`1080p30`（默认）或 `2160p30`（4K） |

## 3. 配音与时长校准

```bash
cd production && .venv/bin/python tts.py            # 全部；也可以 tts.py 2-3 4-1 只重做几镜；--force 强制重做
```

每镜得到 `audio/<id>.mp3` 和 `timing/<id>.json`（口播原文、TTS 文本、时长、逐词时间）。最后一行打印预计成片时长。

- 默认音色 `zh-CN-XiaoxiaoNeural`（清新明亮的女声），`+6%` 语速下约 4.2 字/秒。男声可用 `zh-CN-YunxiNeural`（`+0%`）。换音色前先把 `audio/`、`timing/` 备份到 `audio_<音色>/`、`timing_<音色>/`。
- 超出目标时长时，先把语速提高到 `+8%`～`+10%`（再快会显得赶），仍超出就回到脚本删字。改了口播要同时改脚本文件，再重新导出 shots.json 并重做对应镜头的 TTS。
- 听一两镜抽查读音（Read 不能听音频，可以用 `ffmpeg -ss` 截取，交给用户试听；或检查 timing 里的 words 有没有对不上的告警 `cannot align`）。数字、英文缩写、带连字符的词最容易读错，用 `tts_replace` 修。
- 换音色、改语速或改口播后，所有依赖时间的东西都会变：重做 TTS 后要重新渲染受影响的镜头，再重新合成。

## 4. 论文素材

```bash
.venv/bin/python pdf_assets.py extract ../paper.pdf      # 词坐标、400 DPI 页面、内嵌原图、逐页文本
.venv/bin/python pdf_assets.py find 8 "^MVSA$"           # 第 8 页上匹配的词及其坐标（pt）
.venv/bin/python pdf_assets.py box 8 113 120 484 300     # 把一块区域存成 build/box_p8.png，用 Read 看
```

- **表格和正文**用页面渲染图：`Crop(8, (x0, y0, x1, y1), width=7.3)`，坐标单位是 pt（PDF 坐标，原点在左上）。单元格高亮用 `find_word` 拿坐标，再 `crop.rect(box)`，位置精确到字。
- **图**优先用 `pdfimages` 抽出的原图（`assets/figs/img-<页>-<序号>.png`，分辨率通常比页面渲染高）：`Crop("figs/img-003-002.png", (0, 0, W, H), width=12)`，坐标单位是像素。矢量图（pdfimages 抽不到）用页面渲染图裁。
- **在图上叠加标注**（圈出某根柱子、某个点）：先用 Read 看图，再用 NumPy 按颜色找到元素的像素坐标，存成 json 供场景使用，例如：

  ```python
  a = np.asarray(Image.open("assets/fig1.png").convert("RGB")).astype(int)
  m = (np.abs(a - np.array([248, 152, 152])).max(axis=2) <= 10)   # 图例里“Ours”的颜色
  cols = np.where(m.sum(axis=0) > 5)[0]                            # 含该颜色的列 → 柱子的 x 范围
  ```

  然后在场景里用 `crop.pt(x, y)` 把像素坐标换成画面坐标。
- **裁出的图带进了不相干的内容**（相邻公式、别的子图）：用 NumPy 把那部分涂白，另存为 `assets/<名>_clean.png`，例如按椭圆距离做遮罩。改了源图要删 `assets/crops/` 里的缓存。
- **场景插画**（卧室照片、深度图、加噪图）用 `make_assets.py` 程序生成，见 `examples/qmf/make_assets.py`。不要用网上的图片。

## 5. 写镜头

### Shot API（common.py）

```python
from common import *

class S1_2(Shot):
    sid = "1-2"                       # 对应 shots.json 的 id；类名 S1_2，写在 ch1.py

    def body(self):
        tab = Crop(8, (113, 120.5, 484, 300), width=7.3).move_to(LEFT * 3)
        src = self.source("出处：Table 1，MVSA，平均准确率（%）")       # 右上角出处
        self.play_at(self.cue("Table 1"), FadeIn(tab), FadeIn(src), run_time=0.6)
        cell = tab.rect(find_word(8, "75.61"), color=BASELINE)
        self.play_at(self.cue("75.61"), Create(cell), run_time=0.4)
        warn = tag("论文未说明", color=WARN).to_edge(RIGHT)
        self.play_at(self.cue("没定义", end=True), FadeIn(warn), run_time=0.4)
```

| 接口 | 作用 |
|---|---|
| `self.cue(phrase, k=0, end=False, offset=0)` | 口播中第 k 次（从 0 数）出现 `phrase` 的时刻；`end=True` 取念完的时刻。`phrase` 要在 **TTS 文本**里（经过 `tts_replace` 之后） |
| `self.play_at(t, *anims, run_time=…)` | 等到 t 再播放；已经过了 t 会在日志里打印 `late by` |
| `self.at(t)` | 只等待到 t |
| `self.source(text)` | 右上角出处小字（返回对象，自己 FadeIn） |
| `self.clear_stage(keep=…)` | 淡出除进度条和章节标签外的全部对象 |
| `self.length` / `self.end_of_speech()` | 镜头总长 / 口播结束时刻 |
| `carry_out = True` / `carry_in = True` | 本镜结尾不清场 / 下一镜直接接着画（下一镜要在开头 `self.add(...)` 重建同样的对象） |
| `skip_intro = True` | 不播章节标题卡（第一镜 1-1 用：片头卡刚播完，开头 `self.play(FadeIn(self.tagm))`） |
| `T / TB / M / tag / card / hl_box` | 文字、粗体、公式、圆角标签、卡片、高亮框 |
| `Crop(src, box, height|width)`、`.pt / .rect / .veil` | 论文截图、坐标换算、高亮框、留洞的暗幕 |
| `find_word(page, text, x, y, region)`、`union_box` | 找词坐标、合并多个框 |

基类自动处理：底部进度条、左上角章节标签、每章第一镜的章节标题卡（约 2.1 秒）、结尾清场，以及把镜头补齐到精确帧数（音画对齐靠这一步）。

### 布局

- 画面坐标：宽 14.22、高 8（x ∈ [−7.11, 7.11]，y ∈ [−4, 4]）。
- 内容放在 x ∈ [−6.8, 6.8]、y ∈ [−2.75, 3.3]：顶部 0.7 留给章节标签和出处，**底部 1.25 留给烧录字幕**（52 号字，两行时约占 1.2）和进度条。
- 字号：标题 34–56，正文 22–30，注释 17–20。小于 17 在手机上看不清。
- 一屏最多 3 个信息块；新内容进来前，旧的先淡出或缩小移到一边。
- 颜色按角色固定：`ACCENT` 论文方法 / 当前焦点，`BASELINE` 对比基线，`WARN` 存疑、演示值、局限，`GOOD` 正确结果，`ORANGE` 次要强调。

### 同步

- 每个画面变化都挂到口播里的一个词上（`cue`），在观众听到这个词的时候出现。
- `cue` 找不到词会直接报错。重复出现的词用 `k` 指定第几次。
- `run_time` 要小于到下一个 cue 的间隔，否则后面一串都会 `late by`。
- 每章第一镜的前约 2.1 秒是章节标题卡，这段里的第一个 cue 报 `late by ~1.7s` 是正常的；其余的 `late by` 都要修。

### 写法建议

- 一章一个文件。先写一章、预览一章，确认风格后再写下一章，避免整片返工。
- 范例 `examples/qmf/ch*.py` 是完整可用的 26 镜，写之前先读一两个相近的镜头：

| 想做的效果 | 参考 |
|---|---|
| 三栏场景介绍、箭头汇入、最后压暗出问题大字 | `ch1.py` S1_1 |
| 表格截图拆行重排 + 单元格高亮 + 成对柱状图 | `ch1.py` S1_2（`stacked_table1`、`t1_cell`） |
| 图注截图上给关键词画线 | `ch1.py` S1_3 |
| MobjectTable 对比表 | `ch1.py` S1_4、`ch5.py` S5_4 |
| 原图上逐个点亮柱子（像素定位） | `ch1.py` S1_5 |
| 凸函数弦与曲线、ValueTracker 联动 | `ch2.py` S2_2 |
| 长公式分块着色 + Brace 标注各项 | `ch2.py` S2_4 |
| 左右两栏逐项对比 + 散点 | `ch2.py` S2_5 |
| 原图上画圈、暗幕聚焦、两镜连续 | `ch3.py` S3_1 → S3_2 |
| 一步步代入数字的演算 | `ch4.py` S4_2、S4_6 |
| 训练曲线示意 + 留白提问 + 下一镜接着画 | `ch4.py` S4_4 → S4_5 |
| 箱线图拆解、两张子图并排 | `ch5.py` S5_1、S5_2 |
| 局限两栏清单、收尾三张卡片 | `ch5.py` S5_5、S5_6 |

范例里的素材文件（`fig1.png`、`fig2_clean.png`、`fig1_bars.json` 等）属于 QMF 项目，新项目要用自己的素材重做，坐标也要重新量。

## 6. 预览—渲染—合成—质检循环

```bash
./preview.sh ch1 S1_2 3 8 14 20          # 480p 快速渲染，在第 3/8/14/20 秒截帧拼成一张图
```

输出里有 `late by` 告警、报错，以及拼图路径，用 Read 打开拼图检查：文字溢出画面、元素重叠、被字幕区遮挡、截图模糊、高亮框没对准。截帧时间挑每个动画刚完成的时刻。

全部镜头预览通过后：

```bash
./render.sh                               # 全部场景 1080p，4 路并行；日志在 render/<Scene>.log
./render.sh S3_1 S3_2                     # 只重渲几个
.venv/bin/python assemble.py              # 拼接 + 配音 + 字幕 → ../<output>.mp4 与 .srt
.venv/bin/python qa_frames.py             # 每镜截两帧，拼成 build/qa/sheet_*.png
```

渲染 26 镜、约 10 分钟的视频，在 4 核机器上大约需要 10–15 分钟，放后台跑。`render.sh` 结束时会汇总所有 `late by`。

质检要看完所有 `sheet_*.png`，逐镜对照脚本的画面描述。另外随机挑几条字幕，在字幕结束时刻截帧（`ffmpeg -ss <t> -i out.mp4 -frames:v 1 x.png`），确认画面上已经出现口播提到的东西，以此验证音画同步。发现问题就改代码，`render.sh <Scene>` 重渲，再 `assemble.py`。

字幕由 `assemble.py` 根据逐词时间戳自动生成：按标点切分句子，同一句里的短分句会合并，每条字幕在下一条开始前收起，超过 30 字宽时自动折成两行。字幕字号 52，SRT 文件同时输出，方便上传平台使用外挂字幕。

## 7. 输出

| 版本 | 命令 | 说明 |
|---|---|---|
| 成片 | `assemble.py` | H.264 CRF 18，AAC 192k，响度 −16 LUFS，字幕烧录 |
| 不烧字幕 | `assemble.py --no-burn` | 配合 SRT 外挂字幕 |
| 4K | `RES=3840,2160 ./render.sh`，再把 `video.json` 的 `quality` 改成 `2160p30`，然后 `assemble.py` | 渲染时间约为 1080p 的 4 倍；表格小字和公式更锐利 |

Manim 的中间片段在 `manim.cfg` 里设为 CRF 15，最终画质以它为上限。画面多是静态文字，成片码率通常只有几百 kbps，这是正常现象。

## 8. 踩过的坑

| 现象 | 原因与解决 |
|---|---|
| 并行渲染偶发 TeX `ParseError` | 多个进程共用 TeX 缓存。`render.sh` 已给每个场景独立的 `--media_dir` |
| 成片有色块、文字发虚 | Manim 默认中间片段 CRF 23。用模板里的 `manim.cfg`（CRF 15） |
| `KeyError: 'lanczos'` | `RESAMPLING_ALGORITHMS` 里没有 lanczos，用 `"bicubic"` |
| `MobjectTable` 报 `NotImplementedError` | 表格里有空字符串的 Text。改用 `row_labels` / `col_labels`，或用空格占位 |
| `FadeTransform` 作用于含图片的 Group 失败 | 改成新对象 FadeIn、旧对象 FadeOut 后 remove |
| FadeOut 一个 Group 后还有东西留在画面上 | 那个对象是单独 `add` 的，不在 Group 里。显式 FadeOut 它 |
| `M()` 报 multiple values for `size` | `M` 的签名是 `M(*tex, size=…)`，不要把字号当第二个位置参数 |
| 给 Mobject 子类加名叫 `dim` 的方法后行为异常 | `dim` 是 Mobject 已有的属性（维度）。别用这个名字（Crop 用的是 `veil`） |
| 第一镜动画全部晚了约 2 秒 | 第一镜也播了章节标题卡。给 S1_1 设 `skip_intro = True` |
| 公式里的中文显示成方块 | 没用 xeCJK 模板。`from common import *` 会设好默认模板，别在别处另建 TexTemplate |
| `pkill -f manim` 把自己的 shell 也杀了（exit 144） | `-f` 会匹配到命令行里含 manim 的当前 shell。用 `pgrep` 查到 PID 后 `kill <PID>` |
| 字幕跨句合并、两条重叠 | 已在 `assemble.py` 修复：短分句只在同一句内合并，每条在下一条开始前收起 |
| 截图被放大后模糊 | `Crop` 的 `scale_px` 控制采样密度（默认 1.6，图表细节多时用 2.0–2.6），源图来自 400 DPI 页面 |
