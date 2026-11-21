#!/usr/bin/env python3
"""Render meeting.json (written by the AI after analysis) into two files:
  MEETING_SUMMARY.html  a page to double-click: task cards with the clip players built in
  MEETING_SUMMARY.md    the same content as plain text

Usage:
  python3 render_report.py meeting.json [-o MEETING_SUMMARY.md] [--html MEETING_SUMMARY.html] [--clips-dir clips]

See references/output-schema.md for the meeting.json structure.
"""
import argparse
import html as H
import json
from pathlib import Path


def hms(sec):
    if sec is None:
        return "--:--:--"
    sec = int(round(sec))
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1c2330;--mut:#5d6878;--line:#e2e6ec;--acc:#1f6feb;--warn:#b25e00;--warnbg:#fff4e0}
@media (prefers-color-scheme:dark){:root{--bg:#12151b;--card:#1b2029;--ink:#e8ecf2;--mut:#9aa6b6;--line:#2c3440;--acc:#6aa5ff;--warn:#ffc46b;--warnbg:#3a2c12}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.7rem;margin:0 0 4px}h2{font-size:1.2rem;margin:36px 0 12px}
h3{font-size:1.05rem;margin:0 0 8px}.meta{color:var(--mut);font-size:.92rem}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:12px 0}
.who{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.pill{border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:.85rem;color:var(--mut)}
.pill b{color:var(--ink)}.pill.due{border-color:var(--acc);color:var(--acc)}ul{margin:6px 0;padding-left:20px}
blockquote{margin:10px 0;padding:6px 12px;border-left:3px solid var(--acc);color:var(--mut);font-style:italic}
video,audio{width:100%;margin-top:10px;border-radius:8px;background:#000}audio{background:none}
.warn{background:var(--warnbg);color:var(--warn);border-radius:8px;padding:6px 10px;font-size:.9rem;margin-top:8px}
.q{font-weight:600}.a{margin:2px 0 0}.t{color:var(--mut);font-size:.85rem;font-variant-numeric:tabular-nums}
table{width:100%;border-collapse:collapse;font-size:.92rem}td,th{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
.wrap{overflow-x:auto}
"""


def render_html(m, clips_dir):
    e = lambda x: H.escape(str(x if x is not None else ""))

    def player(item):
        c = item.get("clip")
        if not c:
            return ""
        tag = "audio" if c.lower().endswith((".m4a", ".mp3", ".wav")) else "video"
        return f'<{tag} controls preload="metadata" src="{e(clips_dir)}/{e(c)}"></{tag}>'

    o = [f"<!doctype html><html lang='{e(m.get('language','en'))}'><head><meta charset='utf-8'>"
         f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{e(m.get('title','Meeting summary'))}</title>"
         f"<style>{CSS}</style></head><body><main>"]
    o.append(f"<h1>{e(m.get('title','Meeting summary'))}</h1>")
    parts = ", ".join(e(p["name"]) + (f" ({e(p['role'])})" if p.get("role") else "") for p in m.get("participants", []))
    o.append(f"<div class='meta'>{e(m.get('date',''))}{' · ' if m.get('date') and parts else ''}{parts}</div>")
    o.append(f"<h2>What the bosses need</h2><div class='card'>{e(m.get('summary',''))}")
    if m.get("decisions"):
        o.append("<h3 style='margin-top:14px'>Decisions</h3><ul>" + "".join(
            f"<li>{e(d['text'])} <span class='t'>({e(d.get('by','?'))}, {hms(d.get('at'))})</span></li>" for d in m["decisions"]) + "</ul>")
    o.append("</div>")

    tasks = m.get("tasks", [])
    o.append("<h2>Tasks</h2>")
    if tasks:
        o.append("<div class='card wrap'><table><tr><th>#</th><th>Task</th><th>Who does it</th><th>Deadline</th></tr>" + "".join(
            f"<tr><td>{i}</td><td>{e(t['task'])}</td><td>{e(t.get('assignee','unassigned'))}</td><td>{e(t.get('deadline') or '—')}</td></tr>"
            for i, t in enumerate(tasks, 1)) + "</table></div>")
    else:
        o.append("<div class='card'>No explicit task assignments found.</div>")
    for i, t in enumerate(tasks, 1):
        o.append(f"<div class='card'><h3>{i}. {e(t['task'])}</h3><div class='who'>"
                 f"<span class='pill'>Who does it: <b>{e(t.get('assignee','unassigned'))}</b></span>"
                 f"<span class='pill'>Asked by: <b>{e(t.get('assigner','?'))}</b></span>"
                 + (f"<span class='pill due'>Deadline: <b>{e(t['deadline'])}</b></span>" if t.get("deadline") else "")
                 + f"<span class='pill t'>{hms(t.get('start'))}–{hms(t.get('end'))}</span></div>")
        if t.get("what_is_needed"):
            o.append("<b>What is needed</b><ul>" + "".join(f"<li>{e(n)}</li>" for n in t["what_is_needed"]) + "</ul>")
        if t.get("quote"):
            o.append(f"<blockquote>“{e(t['quote'])}”</blockquote>")
        if t.get("confidence") and t["confidence"] != "high":
            o.append(f"<div class='warn'>Please confirm: {e(t.get('confidence_note') or 'the owner or details were not clear in the meeting')}</div>")
        o.append(player(t) + "</div>")

    o.append("<h2>Questions and answers</h2>")
    for q in m.get("qa", []):
        ans = f"<p class='a'>{e(q['answer'])} <span class='t'>— {e(q.get('answered_by','?'))}</span></p>" if q.get("answer") \
            else "<div class='warn'>Not answered in the meeting. Follow up.</div>"
        o.append(f"<div class='card'><div class='q'>{e(q['question'])} <span class='t'>— {e(q.get('asked_by','?'))}, {hms(q.get('at'))}</span></div>{ans}{player(q)}</div>")
    if not m.get("qa"):
        o.append("<div class='card'>No questions recorded.</div>")

    o.append("<h2>Topics, in order</h2>")
    for tp in m.get("topics", []):
        o.append(f"<div class='card'><h3>{e(tp['title'])} <span class='t'>{hms(tp.get('start'))}–{hms(tp.get('end'))}</span></h3>{e(tp.get('summary',''))}")
        if tp.get("exchanges"):
            o.append("<ul>" + "".join(f"<li><b>{e(x.get('speaker','?'))}</b> <span class='t'>{hms(x.get('at'))}</span> {e(x['text'])}</li>" for x in tp["exchanges"]) + "</ul>")
        o.append("</div>")

    if m.get("open_points"):
        o.append("<h2>Unclear points to confirm</h2><div class='card'><ul>" + "".join(f"<li>{e(x)}</li>" for x in m["open_points"]) + "</ul></div>")
    o.append("</main></body></html>")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meeting_json")
    ap.add_argument("-o", "--output", default="MEETING_SUMMARY.md")
    ap.add_argument("--html", default=None, help="default: same name as -o with .html")
    ap.add_argument("--clips-dir", default="clips")
    args = ap.parse_args()

    m = json.loads(Path(args.meeting_json).read_text(encoding="utf-8"))
    out = []
    title = m.get("title") or "Meeting summary"
    out.append(f"# {title}")
    meta = []
    if m.get("date"):
        meta.append(f"**Date:** {m['date']}")
    if m.get("participants"):
        parts = ", ".join(f"{p['name']} ({p['role']})" if p.get("role") else p["name"] for p in m["participants"])
        meta.append(f"**Participants:** {parts}")
    if meta:
        out.append("  \n".join(meta))

    out.append("\n## 1. Summary (what the bosses need)\n")
    out.append(m.get("summary", "").strip())
    if m.get("decisions"):
        out.append("\n**Decisions made:**")
        for d in m["decisions"]:
            out.append(f"- {d['text']} *(by {d.get('by','?')}, {hms(d.get('at'))})*")

    tasks = m.get("tasks", [])
    out.append("\n## 2. Task assignments\n")
    if not tasks:
        out.append("_No explicit task assignments found._")
    else:
        out.append("| # | Task | Assigned to | Assigned by | Deadline | Clip |")
        out.append("|---|------|-------------|-------------|----------|------|")
        for i, t in enumerate(tasks, 1):
            clip = f"[{hms(t.get('start'))}–{hms(t.get('end'))}]({args.clips_dir}/{t.get('clip','')})" if t.get("clip") else f"{hms(t.get('start'))}–{hms(t.get('end'))}"
            out.append(f"| {i} | {t['task']} | {t.get('assignee','unassigned')} | {t.get('assigner','?')} | {t.get('deadline') or '—'} | {clip} |")
        out.append("")
        for i, t in enumerate(tasks, 1):
            out.append(f"### Task {i}: {t['task']}")
            out.append(f"- **Who does it:** {t.get('assignee','unassigned')}")
            out.append(f"- **Who asked:** {t.get('assigner','?')}")
            if t.get("deadline"):
                out.append(f"- **Deadline:** {t['deadline']}")
            if t.get("what_is_needed"):
                out.append("- **What the boss needs (details / acceptance):**")
                for n in t["what_is_needed"]:
                    out.append(f"  - {n}")
            if t.get("quote"):
                out.append(f"- **Said as:** “{t['quote']}”")
            if t.get("clip"):
                out.append(f"- **Clip:** `{args.clips_dir}/{t['clip']}` ({hms(t.get('start'))}–{hms(t.get('end'))})")
            if t.get("confidence") and t["confidence"] != "high":
                out.append(f"- **Confidence:** {t['confidence']} — {t.get('confidence_note','confirm with the assigner')}")
            out.append("")

    out.append("## 3. Questions and answers\n")
    qa = m.get("qa", [])
    if not qa:
        out.append("_No questions recorded._")
    for i, q in enumerate(qa, 1):
        out.append(f"**Q{i} ({q.get('asked_by','?')}, {hms(q.get('at'))}):** {q['question']}")
        if q.get("answer"):
            out.append(f"**A ({q.get('answered_by','?')}):** {q['answer']}")
        else:
            out.append("**A:** _not answered in the meeting — follow up_")
        if q.get("clip"):
            out.append(f"Clip: `{args.clips_dir}/{q['clip']}`")
        out.append("")

    out.append("## 4. Topics, in order (who said what)\n")
    for i, tp in enumerate(m.get("topics", []), 1):
        out.append(f"### {i}. {tp['title']}  ({hms(tp.get('start'))}–{hms(tp.get('end'))})")
        if tp.get("summary"):
            out.append(tp["summary"])
        if tp.get("exchanges"):
            out.append("")
            for e in tp["exchanges"]:
                out.append(f"- **{e.get('speaker','?')}** ({hms(e.get('at'))}): {e['text']}")
        if tp.get("related_tasks"):
            out.append(f"\n_Related tasks: {', '.join(str(x) for x in tp['related_tasks'])}_")
        out.append("")

    if m.get("open_points"):
        out.append("## 5. Unclear points to confirm\n")
        for o in m["open_points"]:
            out.append(f"- {o}")

    Path(args.output).write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    html_path = Path(args.html) if args.html else Path(args.output).with_suffix(".html")
    html_path.write_text(render_html(m, args.clips_dir), encoding="utf-8")
    print(f"wrote {html_path}")


if __name__ == "__main__":
    main()
