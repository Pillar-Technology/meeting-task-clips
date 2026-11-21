#!/usr/bin/env python3
"""Normalize a meeting transcript into segments.json.

Supported inputs (auto-detected):
  * Google Meet transcript exported from the Google Doc as .txt
    (blocks of "HH:MM:SS" lines followed by "Speaker Name: text")
  * .vtt / .srt / .sbv caption files (YouTube / Meet recording captions)
  * Plain "Speaker: text" lines with no timestamps (timestamps left null)

Usage:
  python3 parse_transcript.py <transcript file> [-o segments.json]

Output: a JSON list, one item per spoken turn:
  {"id": 12, "start": 754.0, "end": 761.5, "speaker": "Rina", "text": "..."}
Times are seconds from the start of the recording. `end` is the next
segment's start when the source has no explicit end time.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TS = r"(\d{1,2}):(\d{2}):(\d{2})(?:[.,](\d{1,3}))?"
TS_SHORT = r"(\d{1,2}):(\d{2})(?:[.,](\d{1,3}))?"


def to_seconds(m, short=False):
    if short:
        mm, ss, ms = m.group(1), m.group(2), m.group(3)
        return int(mm) * 60 + int(ss) + (int(ms.ljust(3, "0")) / 1000 if ms else 0)
    hh, mm, ss, ms = m.group(1), m.group(2), m.group(3), m.group(4)
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + (int(ms.ljust(3, "0")) / 1000 if ms else 0)


def strip_tags(s):
    # WebVTT voice tag <v Name>text</v> -> "Name: text" so the speaker survives.
    s = re.sub(r"<v(?:\.[^\s>]+)?\s+([^>]+)>", r"\1: ", s)
    return re.sub(r"<[^>]+>", "", s).strip()


def split_speaker(text):
    """'Name: words' -> ('Name', 'words'); otherwise (None, text)."""
    m = re.match(r"^\s*([^:：]{1,60}?)\s*[:：]\s*(.+)$", text, re.S)
    if m:
        name = m.group(1).strip()
        # Real speaker names have no digits or brackets; "Title (2026-11-20 10:00)" is not a speaker.
        if not re.search(r"[\d()\[\]]", name):
            return name, m.group(2).strip()
    return None, text.strip()


def parse_vtt_srt(lines):
    segs = []
    cur = None
    for raw in lines:
        line = raw.rstrip("\n")
        m = re.search(TS + r"\s*-->\s*" + TS, line)
        if m:
            start = to_seconds(re.match(TS, m.group(0)))
            end = to_seconds(re.search(TS + r"$", m.group(0).split("-->")[1].strip()))
            cur = {"start": start, "end": end, "text": []}
            segs.append(cur)
            continue
        m2 = re.search(TS_SHORT + r"\s*-->\s*" + TS_SHORT, line)
        if m2 and cur is None or (m2 and not m):
            a, b = m2.group(0).split("-->")
            cur = {"start": to_seconds(re.match(TS_SHORT, a.strip()), True),
                   "end": to_seconds(re.match(TS_SHORT, b.strip()), True), "text": []}
            segs.append(cur)
            continue
        if cur is None or not line.strip() or line.strip().isdigit() or line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue
        cur["text"].append(strip_tags(line))
    out = []
    for s in segs:
        text = " ".join(t for t in s["text"] if t)
        # VTT voice tags <v Name> become "Name: text" after strip; handle both.
        spk, body = split_speaker(text)
        out.append({"start": s["start"], "end": s["end"], "speaker": spk, "text": body})
    return out


def parse_sbv(lines):
    segs, cur = [], None
    for raw in lines:
        line = raw.rstrip("\n")
        m = re.match(r"^(\d+:\d{2}:\d{2}[.,]\d+),(\d+:\d{2}:\d{2}[.,]\d+)$", line.strip())
        if m:
            cur = {"start": to_seconds(re.match(TS, m.group(1))),
                   "end": to_seconds(re.match(TS, m.group(2))), "text": []}
            segs.append(cur)
        elif cur and line.strip():
            cur["text"].append(line.strip())
    out = []
    for s in segs:
        spk, body = split_speaker(" ".join(s["text"]))
        out.append({"start": s["start"], "end": s["end"], "speaker": spk, "text": body})
    return out


def parse_meet_doc(lines, wps=2.5):
    """Google Meet transcript (Doc export). Timestamp lines mark the time of
    the following speaker turns; 'Name: text' lines are turns, continuation
    lines are appended to the previous turn."""
    segs = []
    current_time = None
    last_speaker = None
    started = False
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if not started:
            # Skip the header (title, "Attendees", names) until "Transcript" or the first timestamp/turn.
            if line.lower() in ("transcript", "transcription") or re.fullmatch(TS, line):
                started = True
                if line.lower().startswith("transcrip"):
                    continue
            elif split_speaker(line)[0] and len(line) > 3:
                started = True
            else:
                continue
        m = re.fullmatch(TS, line)
        if m:
            current_time = to_seconds(m)
            continue
        m = re.fullmatch(TS_SHORT, line)
        if m:
            current_time = to_seconds(m, True)
            continue
        if line.lower().startswith("this editable transcript") or line.lower().startswith("meeting ended"):
            continue
        spk, body = split_speaker(line)
        if spk:
            last_speaker = spk
            segs.append({"start": current_time, "end": None, "speaker": spk, "text": body})
        elif segs:
            segs[-1]["text"] += " " + body
        else:
            segs.append({"start": current_time, "end": None, "speaker": last_speaker, "text": body})
    # Turns that share one timestamp block: spread them evenly up to the next timestamp.
    i = 0
    n = len(segs)
    while i < n:
        j = i
        while j + 1 < n and segs[j + 1]["start"] == segs[i]["start"]:
            j += 1
        block_start = segs[i]["start"]
        next_start = segs[j + 1]["start"] if j + 1 < n else None
        if block_start is not None and next_start is None:
            # Last block: no closing timestamp, estimate from speaking rate.
            next_start = block_start + sum(max(1.0, len(s["text"].split()) / wps) for s in segs[i:j + 1])
        if block_start is not None and next_start is not None and j > i:
            total_chars = sum(len(s["text"]) for s in segs[i:j + 1]) or 1
            t = block_start
            for s in segs[i:j + 1]:
                s["start"] = round(t, 2)
                t += (next_start - block_start) * len(s["text"]) / total_chars
        i = j + 1
    return segs


def detect(text, suffix):
    if suffix == ".sbv":
        return "sbv"
    if suffix in (".vtt", ".srt") or "-->" in text:
        return "vtt"
    return "doc"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript")
    ap.add_argument("-o", "--output", default="segments.json")
    ap.add_argument("--words-per-second", type=float, default=2.5,
                    help="used to estimate `end` for the last turn and for sources without end times")
    args = ap.parse_args()

    path = Path(args.transcript)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    kind = detect(text, path.suffix.lower())
    segs = parse_meet_doc(lines, args.words_per_second) if kind == "doc" else \
        {"sbv": parse_sbv, "vtt": parse_vtt_srt}[kind](lines)

    # Fill missing end times with the next start, estimate the last one.
    for idx, s in enumerate(segs):
        s["id"] = idx
        if s["end"] is None:
            nxt = segs[idx + 1]["start"] if idx + 1 < len(segs) else None
            if nxt is not None and s["start"] is not None:
                s["end"] = nxt
            elif s["start"] is not None:
                s["end"] = round(s["start"] + max(2.0, len(s["text"].split()) / args.words_per_second), 2)
        s["text"] = re.sub(r"\s+", " ", s["text"]).strip()
    segs = [s for s in segs if s["text"]]

    Path(args.output).write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    speakers = sorted({s["speaker"] for s in segs if s["speaker"]})
    has_time = sum(1 for s in segs if s["start"] is not None)
    print(f"format={kind} segments={len(segs)} with_timestamps={has_time} speakers={speakers}", file=sys.stderr)
    print(f"wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
