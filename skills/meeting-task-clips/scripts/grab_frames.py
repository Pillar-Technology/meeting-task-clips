#!/usr/bin/env python3
"""Save still images from the recording so the AI can look at the meeting.

Usage:
  python3 grab_frames.py recording.mp4 --at 61.9 384 570 [--out frames]
  python3 grab_frames.py recording.mp4 --every 300 [--out frames]

Why: Google Meet shows the active speaker's name on screen, and shared slides or
documents explain what "this page" or "that number" meant. Looking at a frame from
the moment a task was given answers both.
Prints one line per image: "<seconds>\t<path>".
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def duration(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--at", type=float, nargs="*", default=[], help="times in seconds")
    ap.add_argument("--every", type=float, help="one frame every N seconds across the whole video")
    ap.add_argument("--out", default="frames")
    ap.add_argument("--width", type=int, default=1280)
    args = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("FFMPEG_MISSING")
    times = list(args.at)
    if args.every:
        t, d = 0.0, duration(args.video)
        while t < d:
            times.append(t)
            t += args.every
    if not times:
        sys.exit("give --at or --every")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for t in sorted(set(times)):
        target = out / f"frame-{int(t):06d}s.jpg"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", args.video,
                            "-frames:v", "1", "-vf", f"scale='min({args.width},iw)':-2", "-q:v", "3", str(target)],
                           capture_output=True, text=True)
        if r.returncode == 0 and target.exists():
            print(f"{t:.1f}\t{target}")
        else:
            print(f"{t:.1f}\tFAILED {r.stderr.strip()[:120]}", file=sys.stderr)


if __name__ == "__main__":
    main()
