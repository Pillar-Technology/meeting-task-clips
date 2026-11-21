#!/usr/bin/env python3
"""Download a meeting recording or transcript from a Google Drive / Docs link.

Usage:
  python3 fetch_input.py "<link>" [--out DIR]

Works without any login for files shared as "Anyone with the link".
Prints one JSON line on stdout: {"path": "...", "kind": "video|audio|transcript|other"}

Exit codes (so the caller knows what to tell the user):
  0 ok
  3 the link is a folder, not a file
  4 no access (file is private: sharing must be "Anyone with the link",
    or the user downloads the file and sends it instead)
  5 not a recognised Google Drive / Docs link, or network error
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (meeting-task-clips)"}
VIDEO = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
AUDIO = {".m4a", ".mp3", ".wav", ".aac", ".ogg", ".flac"}
TEXT = {".txt", ".vtt", ".srt", ".sbv", ".docx", ".md"}


def classify(url):
    """-> (kind, id) where kind is doc | file | folder | None"""
    m = re.search(r"docs\.google\.com/document/(?:u/\d+/)?d/([\w-]{20,})", url)
    if m:
        return "doc", m.group(1)
    if re.search(r"drive\.google\.com/drive/(?:u/\d+/)?folders/", url):
        return "folder", None
    m = re.search(r"drive\.google\.com/file/(?:u/\d+/)?d/([\w-]{20,})", url) or \
        re.search(r"[?&]id=([\w-]{20,})", url)
    if m and "google.com" in url:
        return "file", m.group(1)
    return None, None


def filename_from(resp, fallback):
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r"filename\*=UTF-8''([^;]+)", cd)
    if m:
        return urllib.parse.unquote(m.group(1))
    m = re.search(r'filename="?([^";]+)"?', cd)
    if m:
        return m.group(1).encode("latin-1", "ignore").decode("utf-8", "ignore") or fallback
    return fallback


def safe(name):
    return re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", name).strip() or "download"


def open_url(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)


def save(resp, out_dir, fallback):
    name = safe(filename_from(resp, fallback))
    target = out_dir / name
    total = int(resp.headers.get("Content-Length") or 0)
    done = 0
    with open(target, "wb") as f:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r  downloading {done >> 20}/{total >> 20} MB", end="", file=sys.stderr)
    print("", file=sys.stderr)
    return target


def is_html(resp):
    return "text/html" in resp.headers.get("Content-Type", "")


def fetch_doc(doc_id, out_dir):
    try:
        resp = open_url(f"https://docs.google.com/document/d/{doc_id}/export?format=txt")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404):
            return None
        raise
    if is_html(resp) or "accounts.google.com" in resp.geturl():
        return None
    return save(resp, out_dir, "transcript.txt")


def fetch_file(file_id, out_dir):
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    try:
        resp = open_url(url)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404):
            return None
        raise
    if is_html(resp):
        # Either a sign-in page (private) or the "can't scan for viruses" confirmation form.
        page = resp.read(400000).decode("utf-8", "replace")
        form = re.search(r'<form[^>]+action="([^"]+)"', page)
        if not form or "accounts.google.com" in resp.geturl():
            return None
        params = dict(re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', page))
        if "id" not in params:
            return None
        try:
            resp = open_url(html.unescape(form.group(1)) + "?" + urllib.parse.urlencode(params))
        except urllib.error.HTTPError:
            return None
        if is_html(resp):
            return None
    return save(resp, out_dir, f"{file_id}.mp4")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("link")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    kind, fid = classify(args.link)
    if kind is None:
        print("NOT_A_DRIVE_LINK: expected a drive.google.com/file/... or docs.google.com/document/... link", file=sys.stderr)
        sys.exit(5)
    if kind == "folder":
        print("FOLDER_LINK: this is a folder. Ask for the link to the recording file itself "
              "(right-click the video in Drive > Share > Copy link).", file=sys.stderr)
        sys.exit(3)
    try:
        path = fetch_doc(fid, out_dir) if kind == "doc" else fetch_file(fid, out_dir)
    except Exception as e:  # network trouble
        print(f"NETWORK_ERROR: {e}", file=sys.stderr)
        sys.exit(5)
    if path is None:
        print("NO_ACCESS: the file is private. Ask the user to either (1) open the file in Drive > Share > "
              "General access > 'Anyone with the link', then send the link again, or (2) download the file "
              "and send it directly.", file=sys.stderr)
        sys.exit(4)
    ext = path.suffix.lower()
    k = "video" if ext in VIDEO else "audio" if ext in AUDIO else "transcript" if ext in TEXT or kind == "doc" else "other"
    print(json.dumps({"path": str(path), "kind": k}))


if __name__ == "__main__":
    main()
