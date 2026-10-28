"""Check a paper-video script, recompute its counts and timecodes, and export shots.json.

Usage:
  python script_tool.py check <script.md> [--target-min 10] [--write]
      per-shot spoken length, symbol / clause / appendix checks, chapter table, length estimate.
      --write rewrites the shot / chapter / title headings with the recomputed counts and timecodes.
  python script_tool.py shots <script.md> <production/shots.json>
      export narration for tts.py: [{id, chapter, text, tail}]

Script format (see references/script-format.md):
  ## 第一章 开场与痛点（00:00–01:39，397 字）
  ### 1-1｜00:00–00:20｜78 字            (optional suffix "（末尾留白 2 秒）" adds a silent tail)
  **口播**：one paragraph of narration
  **画面**：visual direction, optional ```latex blocks
  ## 附录① 数字核对表 / ## 附录② 存疑点清单
"""
import json
import re
import sys
from pathlib import Path

CPS = 4.0          # script convention: 4 spoken syllables per second (240 per minute)
TTS_CPS = 4.2      # measured: zh-CN-XiaoxiaoNeural at +6%
SHOT_GAP = 0.8     # LEAD + TAIL silence per shot in the video
INTRO_OUTRO = 8.0

D = "零一二三四五六七八九"


# ---------------------------------------------------------------- spoken length
def _sec4(x):
    s, zero = "", False
    for p, u in ((1000, "千"), (100, "百"), (10, "十"), (1, "")):
        d = x // p % 10
        if d == 0:
            zero = bool(s)
        else:
            if zero:
                s += "零"
                zero = False
            s += D[d] + u
    return s


def zh_int(n):
    if n == 0:
        return "零"
    parts, i = [], 0
    while n > 0:
        parts.append((n % 10000, ["", "万", "亿", "万亿"][i]))
        n //= 10000
        i += 1
    s, need_zero = "", False
    for sec, u in reversed(parts):
        if sec == 0:
            need_zero = bool(s)
            continue
        if s and (need_zero or sec < 1000):
            s += "零"
        s += _sec4(sec) + u
        need_zero = False
    return s[1:] if s.startswith("一十") else s


def number_len(tok):
    pct = tok.endswith("%")
    tok = tok.rstrip("%")
    ip, _, fp = tok.partition(".")
    if len(ip) > 1 and ip.startswith("0"):
        n = len(ip)                                  # digit by digit
    elif len(ip) == 4 and 1900 <= int(ip) <= 2099 and not fp:
        n = 4                                        # a year: 二零二三
    else:
        n = len(zh_int(int(ip)))
    if fp:
        n += 1 + len(fp)                             # 点 + digits
    return n + (3 if pct else 0)                     # 百分之


def syllables(word):
    if len(word) >= 2 and word.isupper():
        return len(word)                             # acronym: letter by letter
    total = 0
    for part in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", word) or [word]:
        if part.isupper() and len(part) >= 2:
            total += len(part)
            continue
        p = part.lower()
        n = len(re.findall(r"[aeiouy]+", p))
        if p.endswith("e") and not p.endswith("le") and n > 1:
            n -= 1
        total += max(1, n)
    return total


TOKEN = re.compile(r"\d+(?:\.\d+)?%?|[A-Za-z]+|[㐀-鿿〇]|[Ͱ-Ͽ]|.", re.S)


def spoken_len(text):
    n = 0
    for m in TOKEN.finditer(text):
        t = m.group(0)
        if t[0].isdigit():
            n += number_len(t)
        elif t[0].isascii() and t[0].isalpha():
            n += syllables(t)
        elif "㐀" <= t <= "鿿" or t == "〇" or "Ͱ" <= t <= "Ͽ":
            n += 1
    return n


def vwidth(s):
    return sum(0.55 if ord(ch) < 128 else 1.0 for ch in s)


# ---------------------------------------------------------------- parsing
CH_RE = re.compile(r"^## (第\S+?章)\s*(.+?)\s*(?:（[^（）]*）)?\s*$")
SHOT_RE = re.compile(r"^### (\d+-\d+)\s*｜(.*)$")


def parse(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    shots, chapters, cur_ch, cur = [], [], None, None
    field = None
    for i, line in enumerate(lines):
        m = CH_RE.match(line)
        if m and not line.startswith("## 附录"):
            cur_ch = {"head": m.group(1), "title": m.group(2), "line": i, "shots": []}
            chapters.append(cur_ch)
            cur, field = None, None
            continue
        if line.startswith("## "):
            cur_ch, cur, field = None, None, None
            continue
        m = SHOT_RE.match(line)
        if m:
            tail = re.search(r"留白\s*(\d+(?:\.\d+)?)\s*秒", m.group(2))
            declared = re.search(r"｜\s*(\d+)\s*字", line)
            cur = {"id": m.group(1), "line": i, "chapter": f"{cur_ch['head']} {cur_ch['title']}" if cur_ch else "",
                   "tail": float(tail.group(1)) if tail else 0.0,
                   "declared": int(declared.group(1)) if declared else None, "say": [], "see": []}
            shots.append(cur)
            if cur_ch:
                cur_ch["shots"].append(cur)
            field = None
            continue
        if cur is None:
            continue
        if line.startswith("**口播**"):
            field = "say"
            line = re.sub(r"^\*\*口播\*\*[：:]\s*", "", line)
        elif line.startswith("**画面**"):
            field = "see"
            line = re.sub(r"^\*\*画面\*\*[：:]\s*", "", line)
        if field:
            cur[field].append(line)
    for s in shots:
        s["chapter"] = unescape_md(s["chapter"])
        s["text"] = unescape_md("".join(l.strip() for l in s["say"]).strip())
        s["visual"] = "\n".join(s["see"]).strip()
        s["n"] = spoken_len(s["text"])
    return lines, chapters, shots


def unescape_md(s):
    return re.sub(r"\\([*_`#\[\]|\\])", r"\1", s)


def mmss(t):
    t = int(round(t))
    return f"{t // 60:02d}:{t % 60:02d}"


# ---------------------------------------------------------------- commands
SYMBOLS = re.compile(r"[\\$^_{}=<>≤≥≠±×÷∑∏∫√∞∈∉⊂⊆∀∃→←↔⇒↑↓≈∝∂∇𝔼𝒪𝔑ℓͰ-Ͽ⁰-₟]")


def check(path, target_min=10.0, write=False):
    lines, chapters, shots = parse(path)
    text = "\n".join(lines)
    warn = []
    if not shots:
        sys.exit("no shots found: headings must look like '### 1-1｜00:00–00:20｜78 字'")
    # ids
    for ch_i, ch in enumerate(chapters, 1):
        for k, s in enumerate(ch["shots"], 1):
            if s["id"] != f"{ch_i}-{k}":
                warn.append(f"{s['id']}: expected id {ch_i}-{k} (chapter {ch_i}, shot {k})")
    t = 0.0
    rows = []
    for s in shots:
        if not s["text"]:
            warn.append(f"{s['id']}: empty 口播")
        if not s["visual"]:
            warn.append(f"{s['id']}: empty 画面")
        bad = sorted(set(SYMBOLS.findall(s["text"])))
        if bad:
            warn.append(f"{s['id']}: symbols in 口播 {''.join(bad)} — say them in words, put formulas in 画面")
        if s["text"] and s["text"][-1] not in "。？！”":
            warn.append(f"{s['id']}: 口播 should end with 。？！")
        for clause in re.split(r"[，。；：？！]", s["text"]):
            if vwidth(clause) > 48:
                warn.append(f"{s['id']}: clause too long for a 2-line subtitle ({vwidth(clause):.0f}): {clause[:24]}…")
        if s["n"] < 25 or s["n"] > 160:
            warn.append(f"{s['id']}: {s['n']} 字 — shots read best at 40–150 字")
        if s["declared"] is not None and abs(s["declared"] - s["n"]) > max(4, 0.08 * s["n"]):
            warn.append(f"{s['id']}: heading says {s['declared']} 字, counted {s['n']} (run with --write to fix)")
        dur = s["n"] / CPS + s["tail"]
        s["t0"], s["t1"] = t, t + dur
        t += dur
        rows.append(s)
    total_n = sum(s["n"] for s in shots)
    est_video = INTRO_OUTRO + sum(s["n"] / TTS_CPS + SHOT_GAP + s["tail"] for s in shots)

    # numbers in narration that the number checklist does not mention
    appendix = text[text.find("## 附录"):] if "## 附录" in text else ""
    if "数字核对" not in appendix:
        warn.append("missing appendix: ## 附录① 数字核对表")
    if "存疑" not in appendix:
        warn.append("missing appendix: ## 附录② 存疑点清单")
    missing_nums = []
    for s in shots:
        for num in re.findall(r"\d+(?:\.\d+)?", s["text"]):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?![\d])", appendix):
                missing_nums.append(f"{s['id']}:{num}")
    if missing_nums:
        warn.append("numbers in 口播 not found in the appendix: " + ", ".join(missing_nums))

    print(f"{'shot':6s} {'timecode':13s} {'字':>4s} {'decl':>5s}")
    for s in rows:
        print(f"{s['id']:6s} {mmss(s['t0'])}–{mmss(s['t1'])} {s['n']:4d} {str(s['declared'] or '-'):>5s}"
              + (f"  +{s['tail']:g}s" if s["tail"] else ""))
    print("\n| 章节 | 时间码 | 口播字数 | 时长 |\n| --- | --- | --- | --- |")
    for ch in chapters:
        if not ch["shots"]:
            continue
        a, b = ch["shots"][0]["t0"], ch["shots"][-1]["t1"]
        n = sum(s["n"] for s in ch["shots"])
        d = int(round(b)) - int(round(a))
        print(f"| {ch['head'][1:-1]} {ch['title']} | {mmss(a)}–{mmss(b)} | {n} | {d // 60} 分 {d % 60} 秒 |")
    print(f"| 合计 | 00:00–{mmss(t)} | {total_n} | {int(round(t)) // 60} 分 {int(round(t)) % 60} 秒 |")
    print(f"\n{len(shots)} shots, {total_n} 字; script timecodes at {CPS:g} 字/秒: {mmss(t)}; "
          f"expected video at {TTS_CPS:g} 字/秒 + gaps + intro/outro: {mmss(est_video)} (target ≤ {target_min:g} min)")
    if est_video > target_min * 60:
        over = (est_video - target_min * 60) * TTS_CPS
        warn.append(f"expected video {mmss(est_video)} exceeds {target_min:g} min: cut about {over:.0f} 字")
    print("\nwarnings:" if warn else "\nno warnings")
    for w in warn:
        print("  -", w)

    if write:
        out = list(lines)
        for s in shots:
            suffix = f"（末尾留白 {s['tail']:g} 秒）" if s["tail"] else ""
            out[s["line"]] = f"### {s['id']}｜{mmss(s['t0'])}–{mmss(s['t1'])}｜{s['n']} 字{suffix}"
        for ch in chapters:
            if ch["shots"]:
                n = sum(s["n"] for s in ch["shots"])
                out[ch["line"]] = (f"## {ch['head']} {ch['title']}（{mmss(ch['shots'][0]['t0'])}–"
                                   f"{mmss(ch['shots'][-1]['t1'])}，{n} 字）")
        for i, l in enumerate(out):
            if l.startswith("# "):
                tt = int(round(t))
                out[i] = re.sub(r"（[^（）]*分[^（）]*）\s*$", "", l).rstrip() + f"（{tt // 60} 分 {tt % 60} 秒）"
                break
        Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"\nrewrote headings in {path}; paste the chapter table above into 制作说明")
    return not warn


def export_shots(path, out):
    _, _, shots = parse(path)
    data = [{"id": s["id"], "chapter": s["chapter"], "text": s["text"], "tail": s["tail"]} for s in shots]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(data)} shots to {out}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "check":
        tm = float(a[a.index("--target-min") + 1]) if "--target-min" in a else 10.0
        ok = check(a[1], tm, "--write" in a)
        sys.exit(0 if ok else 1)
    elif len(a) == 3 and a[0] == "shots":
        export_shots(a[1], a[2])
    else:
        sys.exit(__doc__)
