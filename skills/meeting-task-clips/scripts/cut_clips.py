#!/usr/bin/env python3
"""Cut video (or audio) clips for every task / Q&A in meeting.json using ffmpeg.

Usage:
  python3 cut_clips.py meeting.json --video recording.mp4 [--out clips] [--pad 3]
                       [--segments segments.json] [--burn-subtitles] [--audio-only]

For each item that has `start`/`end` it writes:
  clips/<NN>-<kind>-<slug>.mp4   (stream copy, fast, no re-encode)
  clips/<NN>-<kind>-<slug>.srt   (the transcript lines inside the clip, if --segments given)
and fills the item's `clip` field in meeting.json so the report can link to it.
--burn-subtitles re-encodes with the subtitles drawn into the picture
(slower, needs an ffmpeg built with libass).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def slug(s, n=40):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:n].rstrip("-") or "clip"


def srt_time(sec):
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def write_srt(path, segments, start, end):
    lines, n = [], 1
    for s in segments:
        if s.get("start") is None or s["end"] <= start or s["start"] >= end:
            continue
        a, b = max(s["start"], start) - start, min(s["end"], end) - start
        spk = f"{s['speaker']}: " if s.get("speaker") else ""
        lines += [str(n), f"{srt_time(a)} --> {srt_time(b)}", spk + s["text"], ""]
        n += 1
    path.write_text("\n".join(lines), encoding="utf-8")
    return n - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meeting_json")
    ap.add_argument("--video", required=True, help="Google Meet recording (.mp4) or an audio file")
    ap.add_argument("--out", default="clips")
    ap.add_argument("--pad", type=float, default=3.0, help="seconds of context before/after")
    ap.add_argument("--segments", help="segments.json, to write an .srt next to each clip")
    ap.add_argument("--burn-subtitles", action="store_true")
    ap.add_argument("--audio-only", action="store_true", help="write .m4a instead of video")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. Install it (brew install ffmpeg / apt install ffmpeg) or skip clipping.")

    mpath = Path(args.meeting_json)
    m = json.loads(mpath.read_text(encoding="utf-8"))
    segments = json.loads(Path(args.segments).read_text(encoding="utf-8")) if args.segments else []
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    items = [("task", t, t["task"]) for t in m.get("tasks", [])] + \
            [("qa", q, q["question"]) for q in m.get("qa", [])] + \
            [("decision", d, d["text"]) for d in m.get("decisions", [])]

    n_done = 0
    for i, (kind, item, label) in enumerate(items, 1):
        if item.get("start") is None or item.get("end") is None:
            continue
        start = max(0.0, item["start"] - args.pad)
        end = item["end"] + args.pad
        ext = "m4a" if args.audio_only else "mp4"
        name = f"{i:02d}-{kind}-{slug(label)}"
        target = out / f"{name}.{ext}"
        srt = out / f"{name}.srt"
        if segments:
            write_srt(srt, segments, start, end)

        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", args.video]
        if args.audio_only:
            cmd += ["-vn", "-c:a", "aac", "-b:a", "96k"]
        elif args.burn_subtitles and segments:
            # subtitles filter needs the path escaped for ffmpeg's filter parser
            sub = str(srt).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
            cmd += ["-vf", f"subtitles='{sub}'", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac"]
        else:
            cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
        cmd.append(str(target))

        if args.dry_run:
            print(" ".join(cmd))
        else:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"FAILED {name}: {r.stderr.strip()[:300]}", file=sys.stderr)
                continue
        item["clip"] = target.name
        n_done += 1
        print(f"{name}.{ext}  {start:.0f}s-{end:.0f}s")

    if not args.dry_run:
        mpath.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{n_done} clips -> {out}/ ; meeting.json updated with clip names", file=sys.stderr)


if __name__ == "__main__":
    main()
