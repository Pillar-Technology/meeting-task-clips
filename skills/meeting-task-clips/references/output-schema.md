# meeting.json schema

Written by the AI in Job 3, read by `cut_clips.py` and `render_report.py`.
All times are seconds from the start of the recording (floats). Omit `start`/`end`
when the transcript has no timestamps.

```json
{
  "title": "Weekly product sync",
  "date": "2026-11-21",
  "language": "id",
  "participants": [
    {"name": "Pak Budi", "role": "boss / Head of Product"},
    {"name": "Rina", "role": "staff / designer"}
  ],
  "summary": "3-6 sentences: what the boss wants overall and why, the main outcomes.",
  "decisions": [
    {"text": "Launch moves to 5 Dec", "by": "Pak Budi", "at": 812.0, "start": 790.0, "end": 830.0}
  ],
  "tasks": [
    {
      "id": 1,
      "task": "Redesign the pricing page with three tiers",
      "assignee": "Rina",
      "assigner": "Pak Budi",
      "deadline": "Friday 28 Nov",
      "what_is_needed": [
        "Three tiers: Basic, Pro, Enterprise",
        "Use the new brand colours from the Figma file",
        "Show monthly and yearly prices"
      ],
      "quote": "Rina, bisa tolong redesign pricing page-nya jadi tiga tier, selesai Jumat ya.",
      "start": 754.0,
      "end": 831.5,
      "segment_ids": [41, 42, 43, 44],
      "confidence": "high",
      "confidence_note": "",
      "clip": ""
    }
  ],
  "qa": [
    {
      "question": "Do we keep the free plan?",
      "asked_by": "Rina",
      "answer": "Yes, but it is not shown on the pricing page; it stays on the signup flow.",
      "answered_by": "Pak Budi",
      "at": 840.0,
      "start": 838.0,
      "end": 862.0,
      "clip": ""
    }
  ],
  "topics": [
    {
      "title": "Pricing page redesign",
      "start": 740.0,
      "end": 900.0,
      "summary": "One or two sentences.",
      "exchanges": [
        {"speaker": "Pak Budi", "at": 754.0, "text": "Asked for a three-tier pricing page by Friday."},
        {"speaker": "Rina", "at": 840.0, "text": "Asked whether the free plan stays; answer: yes, off the page."}
      ],
      "related_tasks": [1]
    }
  ],
  "open_points": [
    "No owner named for updating the FAQ; Pak Budi said 'someone' should do it."
  ]
}
```

Field notes
- `tasks[].what_is_needed` is the most valuable field for the staff member. Gather the
  details even when they were said minutes before or after the actual request.
- `exchanges[].text` is a paraphrase of what the speaker contributed, not a transcript
  copy; the clip and the transcript hold the exact words.
- `confidence` is `high`, `medium` or `low`. Anything below high prints a warning line in
  the report so the user knows to confirm it.
- `clip` is filled by `cut_clips.py`; leave it empty.
