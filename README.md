# Paper-Video

一个 [Claude Code](https://claude.com/claude-code) 技能（skill）：给它一篇论文 PDF，它会先上网查资料、再写一份逐镜讲解脚本，最后用 Manim 动画、edge-tts 配音和烧录字幕做出一部 10 分钟以内的中文讲解视频，同时生成 B 站上传版。

这个技能是从 QMF 论文（Zhang et al., *Provable Dynamic Fusion for Low-Quality Multimodal Data*, ICML 2023）讲解视频的完整制作过程中整理出来的，主要给 Claude Opus 使用。

## 它会做什么

```
论文 PDF
  │
  ├─ 阶段 1  读原文 + 网络检索   → research.md
  │          正式版本、官方代码、审稿意见、作者讲解、后续工作与批评；
  │          论文地图、数字表（带原文位置）、存疑点表
  │
  ├─ 阶段 2  写视频脚本          → <短名> 论文讲解视频脚本（约 N 分钟）.md
  │          按 ljg-paper 的讲论文思路：讲清做了什么、为什么要修正原有认识、
  │          让观众能自己解释结果；逐镜“口播 + 画面”，附数字核对表和存疑点清单；
  │          格式与时长检查、数字复核、新上下文子代理做独立观看检查
  │
  ├─ 阶段 3  配音与素材          edge-tts 逐镜配音（含逐词时间戳）；
  │                              PDF 词坐标、400 DPI 页面、内嵌原图
  │
  ├─ 阶段 4  写镜头              每镜一个 Manim 场景，动画挂在口播的词上同步出现；
  │                              原文表格/图截图 + 精确到单元格的高亮
  │
  └─ 阶段 5  渲染、合成、质检     → <output>.mp4、.srt、<output>_B站上传版.mp4
```

视频的成品标准：外行观众听完能说出论文研究什么、贡献是什么、结论怎样得来、证据支持到哪里为止；视频里的每个数字都能在原文里找到出处；论文没说清的地方直接说出来，不替作者补全。

## 安装

```bash
git clone https://github.com/123aliez/Paper-Video ~/.claude/skills/paper-video
```

装好后在 Claude Code 里用 `/paper-video` 调用，或者直接说需求，例如：

> 把 ~/papers/xxx.pdf 做成论文讲解视频，我要上传到 B 站

> 先只给这篇论文写视频脚本，我看过再做视频

## 运行环境

- Linux（在 Ubuntu 上验证过），能联网（检索资料，以及 edge-tts 调用微软的在线语音服务）
- 系统软件：ffmpeg（需要 libass 和 libx264）、poppler-utils、TeX Live（xelatex + xeCJK）、dvisvgm、Noto Sans CJK 字体、cairo/pango 开发库
- Python 3.12，通过 [uv](https://github.com/astral-sh/uv) 安装：manim、edge-tts、numpy、pillow、scipy

`scripts/setup_env.sh` 会检查以上依赖。有免密 sudo 时它会用 apt 自动安装缺的包，否则只列出缺少的包。

一部 10 分钟的视频大约需要几个小时，大部分时间花在逐镜编写动画上。在 4 核机器上，1080p 渲染约 10–15 分钟。

## 默认设置

| 项目 | 默认 | 怎么改 |
|---|---|---|
| 时长 | ≤ 10 分钟 | 在请求里说明 |
| 观众 | B 站学术区，不熟悉该子领域 | 在请求里说明 |
| 配音 | `zh-CN-XiaoxiaoNeural`，`+6%` | `production/video.json` 的 `voice`、`rate`；男声可用 `zh-CN-YunxiNeural` |
| 读音修正 | 无 | `video.json` 的 `tts_replace`（只改读音，不改字幕） |
| 分辨率 | 1920×1080、30 fps | `RES=3840,2160 ./render.sh`，并把 `quality` 设为 `2160p30` |

## 目录结构

```
paper-video/
├── SKILL.md                    流程总览（Claude 读这个）
├── references/
│   ├── research.md             阶段 1：读原文与网络检索
│   ├── script-guide.md         阶段 2：怎么讲（改写自 ljg-paper）
│   ├── script-format.md        脚本文件格式
│   └── production.md           阶段 3–5：技术栈、Shot API、布局、质检、踩过的坑
├── scripts/
│   ├── setup_env.sh            检查/安装依赖，建 venv
│   ├── init_project.py         从模板创建 production/ 目录
│   └── script_tool.py          脚本检查（字数、时间码、符号、附录）与导出 shots.json
├── templates/                  复制到每个项目的 production/
│   ├── common.py               配色、文字、计时、Shot 基类、论文截图 Crop
│   ├── tts.py                  逐镜配音 + 逐词时间戳
│   ├── pdf_assets.py           词坐标、页面渲染、原图、逐页文本
│   ├── extras.py               片头片尾
│   ├── render.sh  preview.sh   并行渲染 / 低清预览 + 截帧拼图
│   ├── assemble.py             拼接、响度归一、字幕、编码（含 --bilibili）
│   ├── qa_frames.py            成片逐镜截帧拼图
│   ├── manim.cfg  video.json
└── examples/qmf/               完整范例：脚本、26 个镜头的代码、插画生成
```

## 手动使用工具

这些脚本不经过 Claude 也能单独运行：

```bash
python3 scripts/script_tool.py check "脚本.md" --target-min 10 --write   # 检查脚本、重算时间码
python3 scripts/script_tool.py shots "脚本.md" production/shots.json    # 导出口播
cd production
.venv/bin/python tts.py                 # 配音
./preview.sh ch1 S1_2 3 8 14            # 预览单个镜头
./render.sh                             # 全部渲染
.venv/bin/python assemble.py            # 成片 + SRT
.venv/bin/python assemble.py --bilibili # B 站上传版
```

## 说明

- B 站上传版采用两遍编码，目标码率 5800 kbps。讲解视频画面大多是静态的，编码器很早就接近无损，所以实测平均码率通常只有 1–2 Mbps，这是正常现象。B 站的码率上限来自社区整理，不是官方文档。
- `examples/qmf/` 里的截图坐标和素材文件名只适用于 QMF 论文，供参考写法，新论文需要重新量取。仓库不包含论文 PDF 和渲染出的视频。

## 致谢

- 讲论文的思路来自 lijigang 的 [ljg-paper](https://github.com/lijigang/ljg-skills/tree/master/skills/ljg-paper)（MIT License），`references/script-guide.md` 把它改写成了适合视频口播的版本。
- [Manim Community](https://www.manim.community/)、[edge-tts](https://github.com/rany2/edge-tts)、[FFmpeg](https://ffmpeg.org/)、[Poppler](https://poppler.freedesktop.org/)。
