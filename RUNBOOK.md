# Daily runbook — Cogs & Cosmos

This is the procedure the daily scheduled session follows. Times are **IST (Asia/Kolkata)**. Read `data/style_guide.md` and `data/videos.json` before starting.

| Time | Step |
|---|---|
| ~07:40 | Session starts: setup, channel check, research |
| 08:00 | **5 ideas sent** to the owner (message + push notification) |
| by 11:00 | Owner picks one. **No reply by 11:00 → make the top-ranked idea** |
| ~17:30 | Finished video + 3 thumbnails + titles/description/tags sent **for approval** |
| after approval | Upload and schedule for **19:30** |

Format: **a Short every day**, except **Tuesday = one long video (6–8 min)**.

---

## 0. Setup (fresh session)
1. The repo is `Vala412/cogs-cosmos-pipeline`. Run `bash setup.sh` (installs skia-python, kokoro-onnx etc., downloads the voice model from GitHub).
2. Tools you will need: **vidIQ** connector (channel stats, video list, research, title/description/tags/publish time updates) and **Claude in Chrome** (YouTube Studio on the Cogs & Cosmos channel, signed in to the channel owner's Google account: uploads, subtitles, thumbnails, A/B tests, analytics). If either is unavailable, say so plainly in the 8 AM message and continue with what works (web research; files sent for manual upload).

## 1. Channel check (what worked, what didn't)
- vidIQ: `vidiq_user_channels` → channel id (save it in `data/videos.json`), `vidiq_user_videos`, `vidiq_video_stats` / `vidiq_channel_analytics` for each recent video. Or YouTube Studio → Analytics / Content in Chrome.
- For every published video record in `data/videos.json` → `stats`: date, views, impressions CTR, average view duration / % viewed, likes, comments, subscribers gained, A/B test winner if any.
- Write 3–5 bullet **learnings** (e.g. "Shorts with a question hook held 70%+", "map-style thumbnail won the A/B test"). Use them for today's ideas and production.

## 2. Research (every day, fresh)
Do real web searches; don't rely on memory.
- What science / space / technology topics people are curious about **this week** (news, launches, discoveries, trending searches; vidIQ `vidiq_trending_videos`, `vidiq_outliers`, `vidiq_keyword_research`).
- Competitors and top explainer channels: what's outperforming recently (vidIQ outliers / similar channels). Reference set: Kurzgesagt, Veritasium, Primer, Branch Education, minutephysics, LITTLE BIT BETTER, Escaping Ordinary, Psyphoria, Antidote, Becoming More, Stickify. Learn formats, hooks, pacing, visual styles. **Never copy** scripts, characters or artwork.
- Craft: current advice on YouTube scriptwriting and retention (hooks, open loops, pacing), Shorts best practices, and which animation / visual styles audiences respond to.

## 3. Send 5 ideas (by 08:00)
- Must be topics **not already on the channel** (check `data/videos.json` and the channel's video list).
- Fit the channel: science / how things work, with a sci-fi feel.
- For each idea: working title, thumbnail text (curiosity, 2–5 words, no numbers), the 1–2 sentence hook, why now / evidence from research, planned **visual style** (must differ from the last 3 videos), format (Short or Tuesday long).
- Rank them and mark the top pick. Send with `SendUserMessage` and a push notification. Ask the owner to reply with a number.

## 4. Make the video
1. Research the chosen topic properly; fact-check every claim against primary/authoritative sources; keep the source list for the description.
2. Create `episodes/NNN-slug/` with:
   - `script.py`: `LINES = [(scene, beat, spoken_text, caption_or_None, pause_after), ...]`, plus `MOODS`, `STING`, `TWIST`, `FORMAT` ("short"/"long"). See `episodes/001-how-gps-works/script.py`.
   - `scenes.py`: `SCENES = {scene_key: fn(c, t, B, D)}` drawing with `engine/lib.py` helpers (`P`, `since`, `on` timing helpers are defined in the GPS scenes file; copy what you need). Design a **new look** for each episode (palette accents, shapes, motion, layout) while keeping the brand.
   - `thumbs.py`: three thumbnails using `engine/thumbkit.py` (flat, human-designed look).
3. Run, with `EP=episodes/NNN-slug FORMAT=short|long`:
   ```
   python3 engine/tts.py                 # narration per line -> audio/lines/*.wav
   python3 engine/render.py timeline     # scene/beat timings
   python3 engine/render.py stills 3 9 ... # full-size frames at the busiest moments; LOOK at them, fix overlaps/missing glyphs
   python3 engine/render.py scenes       # one mp4 per scene
   python3 engine/mix.py                 # music + SFX + narration, ducked
   python3 engine/srt.py                 # out/captions_en.srt
   python3 engine/finish.py Final.mp4 [--max-mb 3.6]   # Shorts: always --max-mb 3.6
   ```
4. Check: pull 8–12 frames from the final file, loudness about −14 LUFS, captions line up, outro follows the style guide.
5. Write metadata: 3 titles (≤ 60 chars), description (style guide format), tags (≤ 500 chars), hashtags.

## 5. Approval (≈ 17:30)
Send the video, the 3 thumbnails and the metadata (`SendUserFile` + a short message) and a push notification. **Do not upload anything until the owner explicitly approves in this session.** Apply requested changes and re-send.

## 6. Upload (after approval)
- **Short (≤ 3.6 MB):** YouTube Studio in Chrome (Cogs & Cosmos channel) → Create → Upload → file input via `file_upload`. Fill title, description, audience (not for kids), AI-use question (see style guide), category Education, tags, subtitles (.srt), visibility **Schedule 19:30 IST** today.
- **Long video (too big for Chrome's 3.8 MB upload limit):** ask the owner to upload the file as **Private** in Studio; then set title/description/tags/schedule via vidIQ `vidiq_update_video` (privacyStatus "private" + publishAt = 19:30 IST in UTC = 14:00Z) and in Studio (Chrome): main thumbnail, A/B test with the 3 title+thumbnail pairs (needs advanced features), subtitles, playlist, end screen off.
- Confirm in Studio that the video shows as Scheduled for 19:30 with everything filled in.

## 7. Log and push
Add the video to `data/videos.json` (format, topic, style, titles, thumbnails, youtube_id), commit the episode folder (not audio/out), `git push`.
