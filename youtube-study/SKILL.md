---
name: youtube-study
description: Study a YouTube video from a link. Gets a compact transcript, looks only at the frames that matter (code, settings, UI steps), and saves short organized notes to knowledge/. Use whenever the user shares a YouTube link and wants Claude to learn from, summarize, or apply what the video teaches.
---

# YouTube Study (token-saving version)

Turn a YouTube video into short, permanent notes, while using as few tokens as possible.

## Token rules (follow these the whole time)
- Never read raw caption (.vtt) files, meta.json, or long command output. Use the cleanup script and `jq`/`head` to pull only what you need.
- Read the transcript first. Look at frames only where the transcript says something is being shown (code, a menu, a property, "click here", "like this").
- At most **12 frames** per video unless the user asks for more. Look at one frame at a time and stop when you have what you need.
- Write notes short and dense. They get re-read in future sessions, so every extra line costs tokens later.

## Requirements
`yt-dlp`, `ffmpeg`, `python3`, and (only for videos without captions) `whisper`.
If one is missing, tell the user the install command (`brew install <name>`) and stop.

## Steps

1. **Folders**
   - Work folder: `.video-work/` (deleted at the end).
   - Notes folder: `knowledge/videos/<short-slug-of-title>/`.

2. **Basic info** (only title, channel, length, chapters):
   ```
   yt-dlp --skip-download --print "%(title)s | %(channel)s | %(duration_string)s" "<URL>"
   yt-dlp --skip-download --dump-json "<URL>" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(int(c['start_time']), c['title']) for c in (d.get('chapters') or [])]"
   ```

3. **Transcript**
   - Download captions (manual first, then auto-generated):
     ```
     yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" --sub-format vtt -o ".video-work/subs" "<URL>"
     ```
   - Clean them with the script that lives next to this file:
     ```
     python3 ~/.claude/skills/youtube-study/clean_vtt.py .video-work/subs.<lang>.vtt .video-work/transcript.txt
     ```
     (Use `ls .video-work` to find the exact .vtt name. If both manual and auto captions exist, use the manual one.)
   - No captions at all? Transcribe the audio instead:
     ```
     yt-dlp -x --audio-format mp3 -o ".video-work/audio.%(ext)s" "<URL>"
     whisper .video-work/audio.mp3 --model base --output_format txt --output_dir .video-work
     ```
   - Read `transcript.txt`.

4. **Pick the moments to look at**
   From the transcript, list the timestamps where something important is *shown*: code being typed or finished, Explorer/Properties settings, menu clicks. Pick the moment code is **finished**, not while it's being typed.

5. **Grab only those frames** (no full download needed):
   ```
   URL_V=$(yt-dlp -g -f "bv*[height<=720]/b[height<=720]" "<URL>" | head -1)
   ffmpeg -loglevel error -ss <seconds> -i "$URL_V" -frames:v 1 -vf "scale=1280:-1" .video-work/f_<seconds>.jpg
   ```
   Look at each frame. If code is cut off, grab one more frame a few seconds later. Copy code **exactly**; mark unreadable parts `-- [unclear]`. Never invent code that wasn't shown.

6. **Write `knowledge/videos/<slug>/notes.md`** (keep it tight):
   - Source: title, channel, URL, length, date studied
   - Summary (2–4 sentences)
   - Steps to build it (numbered, with timestamps)
   - Code (verbatim; say where each script goes, e.g. ServerScriptService, StarterPlayerScripts, and whether it's a Script, LocalScript or ModuleScript)
   - Roblox setup: services, Explorer hierarchy, important property values
   - Gotchas
   - Unclear / not captured

7. **Update the index**: add one line to `knowledge/INDEX.md` (create it if missing):
   `- [<title>](videos/<slug>/notes.md) — <what it teaches, in under 15 words>`

8. **Clean up**: `rm -rf .video-work`

9. **Report back** in a few sentences: what the video teaches, where the notes are, and anything you couldn't capture. If the project has related scripts, offer to apply what the video taught.

## Answering questions later
Read `knowledge/INDEX.md` first, then open only the one or two notes files that match the question. Don't read every notes file.

## If something fails
- Private, age-restricted, or members-only video: tell the user; don't try workarounds.
- yt-dlp errors: run `brew upgrade yt-dlp` (YouTube changes often), then retry once.
