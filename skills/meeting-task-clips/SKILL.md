---
name: meeting-task-clips
description: Turn a meeting recording or transcript into a clear summary of what the bosses need, a task list (who asked, who must do it, exactly what is needed, deadline), every question with its answer, topics in order with who said what, and short video clips of the moment each task was given. Use this skill whenever the user sends a meeting video, pastes a Google Drive or Google Docs link to a Meet recording or transcript, shares captions or meeting notes (.mp4, .txt, .vtt, .srt), or asks what their boss or manager asked them to do, what the action items were, who was assigned what, or wants clips or highlights of a meeting. Trigger even when they only say "summarize this meeting", "what do I need to do from this call", or paste a drive.google.com link with no other words.
---

# Meeting task clips

Staff often leave a meeting with the bosses unsure what was asked of them. This skill
turns the meeting into one page they can act on, plus clips to replay the exact
instruction in the boss's own words.

**The user is not technical.** They send a video or a Google Drive link and expect an
answer. Never ask them to run a command, export a file, or install something. Do every
step yourself and only come back to them for things only they can do (changing a
file's sharing setting, telling you who is who).

Scripts live in the `scripts/` folder next to this file. Call them by full path, e.g.
`python3 <this-skill-folder>/scripts/parse_transcript.py`. On Windows use `python` if
`python3` is not found.

```
 JOB 1 Get the meeting -> JOB 2 Get the words -> JOB 3 Understand -> JOB 4 Clip -> JOB 5 Report
 link or file             transcript or          tasks, Q&A,         one clip      page + answer
 fetch_input.py           speech-to-text         topics, who         per task      in the chat
                          parse_transcript.py    (your job)          cut_clips.py  render_report.py
                          transcribe.py          grab_frames.py
```

## Job 1: Get the meeting

Make a working folder `meetings/<date>-<short-title>/` in the current directory and put
everything there. What the user gave you decides what to do:

| The user gave | Do this |
|---|---|
| A video or audio file | Use it where it is. |
| A transcript file or pasted text | Save pasted text as `transcript.txt`. |
| A Google Drive / Docs link | If you have a Google Drive tool or connector, use it. Otherwise `python3 scripts/fetch_input.py "<link>" --out <folder>`. |
| Both a recording and a transcript | Best case: use both. |

`fetch_input.py` exit codes and what to tell the user, in plain words:
- `4` (private file): "I can't open that link. In Google Drive, click **Share**, set
  **General access** to **Anyone with the link**, and send it again. Or download the
  video and send me the file."
- `3` (folder link): "That link is a folder. Right-click the video itself, choose
  **Share > Copy link**, and send me that."

If they only sent a recording, check once whether a transcript exists ("Was
transcription turned on in the meeting? If yes, send me that link too; names will be more
accurate") but do not wait for an answer. Carry on with the video.

Roles: if the user did not say who the boss is and who they are, infer it (the boss gives
instructions and approves) and state in your answer that you inferred it.

## Job 2: Get the words

**Transcript available** (the more accurate path, speaker names included):
```bash
python3 scripts/parse_transcript.py transcript.txt -o segments.json
```
Handles Google Meet transcript Docs exported as text, `.vtt`, `.srt`, `.sbv`, and plain
`Name: text` lines.

**Only a recording**:
```bash
python3 scripts/transcribe.py recording.mp4 -o segments.json            # add --language id if known
```
This listens to the recording on the user's own computer. The first run sets itself up
and downloads a speech model, which takes a few minutes; later runs take roughly 5 to 10
minutes per meeting hour. Tell the user it is working and roughly how long, then let it
run. `--model medium` is more accurate for noisy audio or mixed languages and slower;
`--model base` is faster.

Both produce `segments.json`: a list of `{id, start, end, speaker, text}` with times in
seconds. Read the stderr line to see the language, count, and speakers.

## Job 3: Understand the meeting (your job, not a script's)

Read all of `segments.json`. Long meetings can be 1000+ segments; read in chunks, do not
skip. Then write `meeting.json` following `references/output-schema.md`.

**Who is speaking, when the words came from the video.** Speech-to-text gives no names.
Recover them from three sources, in this order of trust:
1. Names used in the conversation. "Rina, can you redesign…" followed by "Okay" means
   the reply is Rina's and the request came from whoever runs the meeting.
2. The picture. Google Meet labels each participant tile and highlights the active
   speaker. Grab frames at the start of the moments that matter (each task request, each
   answer; 10 to 30 frames is plenty, not every segment) and look at them:
   ```bash
   python3 scripts/grab_frames.py recording.mp4 --at 61.9 384 570 --out frames
   ```
3. What the user told you about who is who.
Where you still cannot tell, write "Unidentified speaker" and list it under
`open_points`. A wrong name is worse than an honest blank.

**Use the picture for context too.** If a slide, spreadsheet or design was on screen
while a task was explained, a frame tells you what "this page" or "that number" meant.
Put what you learn into `what_is_needed`.

**What to extract, in order of importance:**
1. **Tasks.** Any moment someone with authority asks someone to do something ("can
   you…", "please…", "I need…", "by Friday…", "who can take…" followed by a volunteer).
   Record the task in one clear sentence, `assignee`, `assigner`, deadline if said,
   `what_is_needed` (details, constraints and acceptance criteria, including ones said
   minutes before or after the request), the exact `quote`, and `start`/`end` covering
   the whole explanation. A good clip runs 20 to 120 seconds: begin where the boss
   starts giving context, end when the assignee acknowledges or the topic changes.
2. **Questions and answers.** Every real question, who asked, who answered, the answer.
   Unanswered questions are open points.
3. **Topics in order**, each with a short summary and what each speaker contributed.
4. **Decisions** stated as final.
5. **Open points**: no clear owner, vague deadline ("soon"), unidentified speaker.

Assignment rules of thumb, because a wrong assignee is the costliest mistake:
- "You" means the person who spoke just before, unless a name was used.
- A task given to a team belongs to the team; note who from it was present.
- Boss asks, someone volunteers: assignee is the volunteer, assigner is the boss.
- If you had to guess, set `confidence: "low"` with a note. The report shows a
  "please confirm" flag.

Write in the language of the meeting unless the user asks otherwise, in plain words.

## Job 4: Cut the clips (when there is a recording)

```bash
python3 scripts/cut_clips.py meeting.json --video recording.mp4 --segments segments.json --out clips
```
One clip per task, question and decision, with 3 seconds of padding, a subtitle file
beside each, and the clip names written back into `meeting.json`. It is a fast stream
copy, seconds even for a two-hour recording. `--audio-only` makes small files for chat
apps, `--pad 8` adds context if a clip starts mid-sentence, `--burn-subtitles` draws
the words into the picture.

Timestamps from a Google Meet transcript Doc are coarse (one per block of several
minutes), so those clips can be off by a few seconds. Timestamps from `transcribe.py`
are accurate to the sentence. When you have both a transcript Doc and the recording and
precise clips matter, run `transcribe.py` as well and take the times from it, keeping
the names from the Doc.

## Job 5: Report

```bash
python3 scripts/render_report.py meeting.json -o MEETING_SUMMARY.md --clips-dir clips
```
Writes `MEETING_SUMMARY.html` (a page with the clip players built in; this is the one
to give the user) and `MEETING_SUMMARY.md`. Read it once as the staff member would and
fix anything unclear in `meeting.json`, then re-render.

**Then answer in the chat itself.** The user should not have to open a file to learn
their tasks. Reply with, in this order: one or two sentences on what the boss wants,
the user's own tasks with deadline and the key details, tasks given to others in one
line each, anything they need to confirm, and last the path to
`MEETING_SUMMARY.html` and the `clips` folder. If your environment can display files or
video, show the summary page.

## Output layout

```
meetings/<date>-<title>/
├── recording.mp4 / transcript.txt   what the user sent
├── segments.json                    Job 2
├── meeting.json                     Job 3
├── frames/                          Job 3, only if you looked at the video
├── clips/                           Job 4
├── MEETING_SUMMARY.html             Job 5, open this
└── MEETING_SUMMARY.md
```

## When something is missing

- **ffmpeg not installed** (needed for clips, frames and listening to video): install it
  for the user (`brew install ffmpeg`, `winget install ffmpeg`, `sudo apt install
  ffmpeg`), telling them in one line what you are doing. If you cannot, and there is a
  transcript, still deliver the summary with timestamps and say clips were skipped.
- **Transcript without timestamps and no recording**: summary only, no clips.
- **Very long or poor audio**: say so, suggest `--model medium`, and mark doubtful
  passages as low confidence rather than inventing words.
- **Several meetings**: one folder per meeting, then offer a combined task list.

`references/output-schema.md` has the exact `meeting.json` fields.
`references/transcript-formats.md` explains the Google Meet file formats.
`assets/example/` shows a finished result.
