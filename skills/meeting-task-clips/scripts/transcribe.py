#!/usr/bin/env python3
"""Turn a meeting recording into segments.json when there is no transcript.

Usage:
  python3 transcribe.py recording.mp4 [-o segments.json] [--model small] [--language id]

Runs speech-to-text locally (nothing is uploaded). The first run sets up a private
Python environment in ~/.cache/meeting-task-clips and downloads the speech model
(a few hundred MB, one time). After that it needs no internet.

Output matches parse_transcript.py: [{"id", "start", "end", "speaker": null, "text"}]
Speakers are unknown at this point; the skill identifies them afterwards from the
video frames and from names used in the conversation.

Models: base (fastest), small (default, good for Indonesian/English), medium (most
accurate, slower). Rough speed on a laptop: small = 5-10 minutes per meeting hour.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CACHE = Path(os.environ.get("MTC_CACHE", Path.home() / ".cache" / "meeting-task-clips"))
VENV = CACHE / "venv"


def venv_python():
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def have_engine():
    for mod in ("faster_whisper", "whisper"):
        try:
            __import__(mod)
            return mod
        except Exception:
            continue
    return None


def bootstrap_and_reexec():
    """Create a private venv with faster-whisper and run this script again inside it."""
    py = venv_python()
    if not py.exists():
        print("First run: setting up speech-to-text (one time, a few minutes)...", file=sys.stderr)
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    probe = subprocess.run([str(py), "-c", "import faster_whisper"], capture_output=True)
    if probe.returncode != 0:
        r = subprocess.run([str(py), "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "faster-whisper"])
        if r.returncode != 0:
            sys.exit("SETUP_FAILED: could not install faster-whisper. Check the internet connection, "
                     "or install it manually: python3 -m pip install faster-whisper")
    env = dict(os.environ, MTC_IN_VENV="1", HF_HUB_DISABLE_PROGRESS_BARS="1")
    sys.exit(subprocess.call([str(py), __file__] + sys.argv[1:], env=env))


def extract_audio(src, dst):
    if not shutil.which("ffmpeg"):
        sys.exit("FFMPEG_MISSING: install ffmpeg (Mac: brew install ffmpeg, Windows: winget install ffmpeg, "
                 "Ubuntu: sudo apt install ffmpeg)")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
                        "-c:a", "pcm_s16le", dst],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"AUDIO_FAILED: {r.stderr.strip()[:300]}")


def run_faster_whisper(wav, model, language):
    import wave
    import numpy as np
    from faster_whisper import WhisperModel
    # Decode the 16 kHz mono wav ourselves: avoids depending on the library's own
    # audio reader, which breaks on some Python / PyAV combinations.
    with wave.open(wav, "rb") as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    m = WhisperModel(model, device="auto", compute_type="int8")
    segs, info = m.transcribe(audio, language=language, vad_filter=True)
    out = []
    for s in segs:
        out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        if len(out) % 50 == 0:
            print(f"  transcribed up to {int(s.end) // 60} min", file=sys.stderr)
    return out, info.language


def run_openai_whisper(wav, model, language):
    import whisper
    r = whisper.load_model(model).transcribe(wav, language=language)
    return [{"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()}
            for s in r["segments"]], r.get("language")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media", help="video or audio file")
    ap.add_argument("-o", "--output", default="segments.json")
    ap.add_argument("--model", default="small")
    ap.add_argument("--language", default=None, help="e.g. id, en. Default: auto-detect")
    args = ap.parse_args()

    if not Path(args.media).exists():
        sys.exit(f"NOT_FOUND: {args.media}")
    engine = have_engine()
    if engine is None:
        if os.environ.get("MTC_IN_VENV"):
            sys.exit("SETUP_FAILED: speech-to-text engine still missing inside the private environment")
        bootstrap_and_reexec()

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        extract_audio(args.media, wav)
        print(f"Transcribing with {engine} ({args.model})...", file=sys.stderr)
        segs, lang = (run_faster_whisper if engine == "faster_whisper" else run_openai_whisper)(wav, args.model, args.language)

    segs = [s for s in segs if s["text"]]
    for i, s in enumerate(segs):
        s.update(id=i, speaker=None)
    Path(args.output).write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"language={lang} segments={len(segs)} speakers=unknown (identify from frames and context)", file=sys.stderr)
    print(f"wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
