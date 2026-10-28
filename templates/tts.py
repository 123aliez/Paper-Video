"""Generate per-shot narration audio with edge-tts and word-level timing.

Usage: python tts.py [shot ids ...] [--force]

Outputs (per shot id, e.g. "1-2"):
  audio/1-2.mp3          narration
  timing/1-2.json        {"display", "tts", "duration", "words": [{t0, t1, c0, c1, text}]}
c0/c1 index into the TTS text; display text and TTS text share punctuation positions.
Voice, rate and pronunciation fixes come from video.json (voice, rate, tts_replace).
"""
import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "video.json").read_text())
VOICE = CFG.get("voice", "zh-CN-XiaoxiaoNeural")
RATE = CFG.get("rate", "+6%")

# Only change how a term is spoken; subtitles keep the script's spelling.
TTS_REPLACE = CFG.get("tts_replace", {})


def tts_text(text: str) -> str:
    for a, b in TTS_REPLACE.items():
        text = text.replace(a, b)
    return text


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]
    )
    return float(out.decode().strip())


def align(text: str, marks):
    """Map each word boundary to a character span of text."""
    words, pos = [], 0
    for t0, dur, w in marks:
        i = text.find(w, pos)
        if i < 0:
            i = text.lower().find(w.lower(), pos)
        if i < 0:
            print(f"  ! cannot align {w!r} after {pos}", file=sys.stderr)
            continue
        words.append({"t0": t0, "t1": t0 + dur, "c0": i, "c1": i + len(w), "text": w})
        pos = i + len(w)
    return words


async def synth(shot, force=False):
    sid = shot["id"]
    text = tts_text(shot["text"])
    key = hashlib.md5(f"{VOICE}|{RATE}|{text}".encode()).hexdigest()
    mp3 = ROOT / "audio" / f"{sid}.mp3"
    tj = ROOT / "timing" / f"{sid}.json"
    if not force and tj.exists() and mp3.exists():
        if json.loads(tj.read_text()).get("key") == key:
            return
    for attempt in range(5):
        try:
            com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
            marks, audio = [], bytearray()
            async for ch in com.stream():
                if ch["type"] == "audio":
                    audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    marks.append((ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]))
            break
        except Exception as e:  # network hiccups
            print(f"  retry {sid}: {e}", file=sys.stderr)
            await asyncio.sleep(2 + attempt * 2)
    else:
        raise RuntimeError(f"TTS failed for {sid}")
    mp3.write_bytes(audio)
    data = {
        "id": sid,
        "key": key,
        "display": shot["text"],
        "tts": text,
        "duration": probe_duration(mp3),
        "words": align(text, marks),
    }
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{sid}: {data['duration']:.2f}s, {len(data['words'])} words")


async def main():
    (ROOT / "audio").mkdir(exist_ok=True)
    (ROOT / "timing").mkdir(exist_ok=True)
    shots = json.loads((ROOT / "shots.json").read_text())
    only = set(sys.argv[1:]) - {"--force"}
    force = "--force" in sys.argv
    for s in shots:
        if only and s["id"] not in only:
            continue
        await synth(s, force=force)
    # estimated final length: intro + outro + per-shot gaps + narration
    tl = 8.0
    for s in shots:
        tj = ROOT / "timing" / f"{s['id']}.json"
        if tj.exists():
            tl += 0.8 + s.get("tail", 0.0) + json.loads(tj.read_text())["duration"]
    print(f"estimated video length {int(tl // 60)}:{tl % 60:05.2f}")


if __name__ == "__main__":
    asyncio.run(main())
