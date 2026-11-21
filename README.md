# Meeting Task Clips

**Send your meeting video or Google Drive link. Get back what your boss asked you to do.**

After a Google Meet with your bosses you get one page with:

- what the bosses want, in plain words
- **your tasks**: what to do, who asked, the deadline, and every detail they mentioned
- every question that was asked, with its answer
- the topics in order, with who said what
- a short **video clip** of each moment a task was given, so you can replay the exact words

Works in **Claude** (Claude Code) and **Codex**.

## Install: paste one sentence

Open Claude or Codex and paste this:

```
Install this skill for me: https://github.com/Pillar-Technology/meeting-task-clips
```

That is the whole installation. The assistant does the rest.

## Use: send the meeting

Send the recording, or paste its Google Drive link, and say who is who:

```
Here is today's meeting: https://drive.google.com/file/d/…/view
Pak Budi is my boss, I am Rina. What do I need to do?
```

You can also drag the video file into the chat instead of a link. If transcription was
turned on in the meeting, paste the transcript link as well. Names will be more accurate.

A few minutes later you get your task list in the chat, plus a summary page
(`MEETING_SUMMARY.html`) and a folder of clips.

**One thing about Drive links:** the assistant can only open a file that is shared as
*Anyone with the link* (in Drive: **Share > General access**). If it is private, the
assistant will tell you, and you can change the setting or just send the video file.

More: [step-by-step guide](docs/GUIDE.md) ·
[how it works (jobs diagram)](docs/HOW_IT_WORKS.md)

---

## For AI assistants: how to install this

The user pasted this repository link and wants the skill installed. Do it for them.
Do not ask them to run commands or click files.

1. Get the repository into a temporary folder:
   `git clone --depth 1 https://github.com/Pillar-Technology/meeting-task-clips`
   (no git: download and unzip
   `https://github.com/Pillar-Technology/meeting-task-clips/archive/refs/heads/main.zip`).
2. Run `python3 install.py` inside it (`python install.py` on Windows). It copies
   `skills/meeting-task-clips/` to `~/.claude/skills/` and/or `~/.codex/skills/`.
   No Python: copy that folder there yourself.
3. If the output says ffmpeg is missing, install it (`brew install ffmpeg`,
   `winget install ffmpeg`, or `sudo apt install -y ffmpeg`). It is needed for video.
4. Tell the user, in one or two plain sentences, that it is installed and that they can
   now send a meeting video or a Google Drive link and say who their boss is.
5. If the user already sent a meeting in the same message, do not make them wait for a
   new chat: read `skills/meeting-task-clips/SKILL.md` and carry on with it now.

Other ways to install, all equivalent:
- Claude Code plugin: `/plugin marketplace add Pillar-Technology/meeting-task-clips`, then
  `/plugin install meeting-task-clips@meeting-task-clips`
- Codex: ask it to install the skill from
  `https://github.com/Pillar-Technology/meeting-task-clips/tree/main/skills/meeting-task-clips`

## What is in this repository

| Path | What |
|---|---|
| `skills/meeting-task-clips/SKILL.md` | the instructions the assistant follows |
| `skills/meeting-task-clips/scripts/` | download from Drive, speech-to-text, transcript parsing, frame grabs, clip cutting, report |
| `skills/meeting-task-clips/assets/example/` | a sample meeting and its finished summary |
| `install.py` | run by the assistant during install |
| `docs/` | user guide and the jobs diagram |

## Privacy

The recording stays on your computer: listening to it and cutting clips happen locally.
Only the text of the meeting is read by the AI model you use. Check your company's rules
before using this on confidential meetings.
