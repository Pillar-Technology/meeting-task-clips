#!/usr/bin/env python3
"""Installs the meeting-task-clips skill for Claude Code and Codex.

This is run by the AI assistant, not by the user:   python3 install.py
It copies skills/meeting-task-clips into the assistant's skills folder and reports
whether ffmpeg (needed for video) is present. Safe to run again to update.
"""
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "skills" / "meeting-task-clips"
HOME = Path.home()
TARGETS = {"claude": HOME / ".claude" / "skills", "codex": HOME / ".codex" / "skills"}


def main():
    if not (SRC / "SKILL.md").exists():
        sys.exit(f"skill folder not found at {SRC}")
    want = [a for a in sys.argv[1:] if a in TARGETS]
    if not want:
        # Install for every assistant that exists on this computer; both if none found yet.
        want = [k for k, p in TARGETS.items() if p.parent.exists()] or list(TARGETS)
    for k in want:
        dest = TARGETS[k] / "meeting-task-clips"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "evals"))
        print(f"installed for {k}: {dest}")
    if shutil.which("ffmpeg"):
        print("ffmpeg: found")
    else:
        print("ffmpeg: MISSING. Install it now for the user: "
              "Mac `brew install ffmpeg`, Windows `winget install ffmpeg`, Ubuntu `sudo apt install -y ffmpeg`")
    print("done. Tell the user: send a meeting video or Google Drive link, and say who the boss is.")


if __name__ == "__main__":
    main()
