"""Mux rendered shots with narration, build subtitles, and encode the final video.

Usage: python assemble.py [--no-burn]
       python assemble.py --bilibili   (re-encode the built video as a high-bitrate upload master)
Reads   render/<Scene>/videos/<module>/<quality>/<Scene>.mp4, audio/, timing/
Writes  ../<output>.mp4, ../<output>.srt, build/subs.ass   (<output> from video.json)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT.parent
BUILD = ROOT / "build"
FPS = 30
SR = 48000
LEAD = 0.25  # must match common.LEAD
FONT = "Noto Sans CJK SC"

SHOTS = json.loads((ROOT / "shots.json").read_text())
CFG = json.loads((ROOT / "video.json").read_text())
NAME = CFG["output"]
QUALITY = CFG.get("quality", "1080p30")  # render.sh resolution folder, e.g. 2160p30 for a 4K render


def segments():
    segs = [("extras", "Intro", None)]
    for s in SHOTS:
        segs.append((f"ch{s['id'].split('-')[0]}", "S" + s["id"].replace("-", "_"), s["id"]))
    segs.append(("extras", "Outro", None))
    return segs


def video_path(mod, scene):
    return ROOT / "render" / scene / "videos" / mod / QUALITY / f"{scene}.mp4"


def frames(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)])
    return int(out.decode().strip())


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ---------------------------------------------------------------- subtitles
SPLIT = re.compile(r"([，。；：？！])")


def raw_spans(text):
    spans, start = [], 0
    for m in SPLIT.finditer(text):
        spans.append((start, m.end()))
        start = m.end()
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def grouping(spans, text):
    """Index groups of clauses shown together. A very short clause joins its neighbour inside the
    same sentence: the next clause if it ends mid-sentence, otherwise the previous one."""
    groups = []
    n = lambda g: sum(spans[j][1] - spans[j][0] for j in g)
    pending = None
    for i, (a, b) in enumerate(spans):
        cur = (pending or []) + [i]
        pending = None
        short = n(cur) < 7
        ends_sentence = text[b - 1] in "。？！"
        if short and not ends_sentence and i + 1 < len(spans):
            pending = cur
            continue
        if short and ends_sentence and groups and text[spans[groups[-1][-1]][1] - 1] not in "。？！" \
                and n(groups[-1]) + n(cur) <= 26:
            groups[-1] += cur
            continue
        groups.append(cur)
    if pending:
        groups.append(pending)
    return groups


def apply_groups(spans, groups):
    return [(spans[g[0]][0], spans[g[-1]][1]) for g in groups]


def clean(s):
    s = s.strip()
    s = re.sub(r"[，。；：、]+$", "", s)
    return re.sub(r"[。；]", "　", s)


def vwidth(s):
    return sum(0.55 if ord(ch) < 128 else 1.0 for ch in s)


def wrap(s, n=30):
    if vwidth(s) <= n:
        return s
    # break near the middle at a natural boundary
    mid = len(s) // 2
    cands = [i for i, ch in enumerate(s) if ch in "，、；：" and 4 < i < len(s) - 4]
    i = min(cands, key=lambda k: abs(k - mid)) + 1 if cands else mid
    return s[:i] + "\\N" + s[i:]


def char_time(words, c):
    """Narration time (s) at character index c of the TTS text, interpolated inside words."""
    for w in words:
        if w["c1"] > c:
            if w["c0"] >= c:
                return w["t0"]
            f = (c - w["c0"]) / max(1, w["c1"] - w["c0"])
            return w["t0"] + f * (w["t1"] - w["t0"])
    return words[-1]["t1"]


def shot_cues(sid, offset):
    tm = json.loads((ROOT / "timing" / f"{sid}.json").read_text())
    disp, tts, words = tm["display"], tm["tts"], tm["words"]
    rd, rt = raw_spans(disp), raw_spans(tts)
    assert len(rd) == len(rt), sid
    groups = grouping(rd, disp)
    dspans, tspans = apply_groups(rd, groups), apply_groups(rt, groups)
    cues = []
    for (d0, d1), (t0c, t1c) in zip(dspans, tspans):
        body = tts[t0c:t1c].rstrip("，。；：？！、")
        a = char_time(words, t0c)
        b = char_time(words, t0c + len(body))
        cues.append([offset + LEAD + a, offset + LEAD + b, clean(disp[d0:d1])])
    # hold each cue until shortly before the next one, never overlapping it
    for a, b in zip(cues, cues[1:]):
        a[1] = min(max(a[1], min(b[0] - 0.05, a[1] + 0.6)), b[0] - 0.03)
    if cues:
        cues[-1][1] += 0.3
    return cues


def ts_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ts_ass(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_subs(all_cues):
    srt = []
    for i, (a, b, s) in enumerate(all_cues, 1):
        srt.append(f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n{s}\n")
    (OUT_DIR / f"{NAME}.srt").write_text("\n".join(srt), encoding="utf-8")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT},52,&H00FFFFFF,&H00FFFFFF,&H00101010,&H64000000,0,0,0,0,100,100,1,0,1,3,1,2,80,80,34,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},Default,,0,0,0,,{wrap(s)}" for a, b, s in all_cues]
    (BUILD / "subs.ass").write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    burn = "--no-burn" not in sys.argv
    BUILD.mkdir(exist_ok=True)
    segs = segments()
    t = 0.0
    concat_v, concat_a, all_cues = [], [], []
    for mod, scene, sid in segs:
        vp = video_path(mod, scene)
        if not vp.exists():
            sys.exit(f"missing render: {vp}")
        n = frames(vp)
        dur = n / FPS
        wav = BUILD / f"{scene}.wav"
        samples = int(round(dur * SR))
        if sid:
            mp3 = ROOT / "audio" / f"{sid}.mp3"
            run(["ffmpeg", "-y", "-i", str(mp3), "-af",
                 f"aresample={SR},adelay={int(LEAD * 1000)}:all=1,apad,atrim=end_sample={samples}",
                 "-ac", "2", "-ar", str(SR), str(wav)])
            all_cues += shot_cues(sid, t)
        else:
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-af",
                 f"atrim=end_sample={samples}", str(wav)])
        concat_v.append(vp)
        concat_a.append(wav)
        print(f"{scene:6s} {dur:7.2f}s  start {t:7.2f}")
        t += dur
    print(f"total {t:.2f}s ({int(t // 60)}:{t % 60:05.2f})")

    (BUILD / "video.txt").write_text("".join(f"file '{p}'\n" for p in concat_v))
    (BUILD / "audio.txt").write_text("".join(f"file '{p}'\n" for p in concat_a))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "video.txt"), "-c", "copy",
         str(BUILD / "video.mp4")])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "audio.txt"),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), str(BUILD / "narration.wav")])
    write_subs(all_cues)

    out = OUT_DIR / f"{NAME}.mp4"
    vf = ["-vf", f"ass={BUILD / 'subs.ass'}"] if burn else []
    run(["ffmpeg", "-y", "-i", str(BUILD / "video.mp4"), "-i", str(BUILD / "narration.wav"), *vf,
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)])
    print("wrote", out)


def encode_bilibili():
    """High-bitrate upload master from the existing build files. Bilibili limits (community sources,
    re-check before relying on them): 1080P average <= 6000 kbps, peak <= 24000 kbps; 4K average
    <= 20000 kbps; AAC <= 320 kbps. Two-pass ABR. Static slides usually saturate far below the
    target (x264 reaches QP ~1), so a low measured average is expected, not a failure."""
    out = OUT_DIR / f"{NAME}_B站上传版.mp4"
    log = str(BUILD / "x264_2pass")
    uhd = QUALITY.startswith("2160")
    rate = ["-level", "5.1", "-b:v", "15000k", "-maxrate", "20000k", "-bufsize", "30000k"] if uhd else \
        ["-level", "4.1", "-b:v", "5800k", "-maxrate", "20000k", "-bufsize", "24000k"]
    common = ["-vf", f"ass={BUILD / 'subs.ass'}", "-c:v", "libx264", "-preset", "slow", "-profile:v", "high",
              *rate, "-g", "300",
              "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
              "-color_range", "tv", "-passlogfile", log]
    run(["ffmpeg", "-y", "-i", str(BUILD / "video.mp4"), *common, "-pass", "1", "-an", "-f", "null", "/dev/null"])
    run(["ffmpeg", "-y", "-i", str(BUILD / "video.mp4"), "-i", str(BUILD / "narration.wav"), *common, "-pass", "2",
         "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "320k", "-ar", str(SR),
         "-movflags", "+faststart", "-shortest", str(out)])
    print("wrote", out)


if __name__ == "__main__":
    if "--bilibili" in sys.argv:
        encode_bilibili()
    else:
        main()
