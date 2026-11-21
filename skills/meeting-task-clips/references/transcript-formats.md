# Google Meet recordings and transcripts: where they are and what they look like

Background for the AI. The user never has to do the export steps below by hand; a
Drive or Docs link is enough and `fetch_input.py` downloads it (a transcript Doc comes
down as plain text automatically).

## Turn on transcript + recording during the meeting
1. In the meeting, click **Activities** (bottom right) > **Transcripts** > **Start transcription**.
2. Optionally **Activities** > **Recording** > **Start recording** for the video.
   (Both need a Google Workspace plan that allows it; the host or organisation admin
   controls this.)
3. Live captions (the CC button) are only shown on screen and are not saved; the saved
   text comes from the Transcripts feature or from the recording's captions.

## Where the files land
- Google Drive of the host > **Meet Recordings** folder.
- Transcript: a Google Doc named `<meeting title> (YYYY-MM-DD HH:MM) - Transcript`.
- Recording: `<meeting title> (YYYY-MM-DD HH:MM).mp4`.
- A link to both is also emailed to the host and the person who started them.

## Export the transcript as text
Open the Doc > **File > Download > Plain text (.txt)**. The result looks like:

```
Weekly sync (2026-11-21 10:00 GMT+7) - Transcript
Attendees
Pak Budi, Rina, Dion
Transcript
00:00:00
Pak Budi: Oke kita mulai ya.
Rina: Siap pak.
00:05:00
Pak Budi: Rina, bisa tolong redesign pricing page...
```

Timestamps appear once per block (roughly every few minutes), not per line. The parser
spreads the lines in a block across the block's duration, weighted by text length, so
clip times are approximate; use `--pad` on `cut_clips.py` to add margin.

## Other accepted formats
- `.vtt`, `.srt`: caption files (YouTube "download captions", Zoom, Teams, Otter exports).
  `<v Name>` voice tags or `Name: text` lines give speaker names.
- `.sbv`: YouTube's own caption format.
- Plain `Name: text` lines with no times (for example pasted from Claude Meetings or a
  chat): summary only, no clips.

## Recording formats
`cut_clips.py` passes the file to ffmpeg, so any container ffmpeg reads works
(`.mp4`, `.mkv`, `.webm`, `.m4a`, `.mp3`). The `--audio-only` option produces small
`.m4a` clips that are easy to send over WhatsApp or Slack.
