# cogs-cosmos-pipeline

Video engine and daily routine for the **Cogs & Cosmos** YouTube channel: original animated explainers drawn in code (skia-python), narrated with Kokoro TTS, with synthesized music, captions and thumbnails.

- `RUNBOOK.md`: the daily procedure (ideas at 8 AM, production, approval, 7:30 PM upload).
- `data/style_guide.md`: brand and the owner's standing rules.
- `data/videos.json`: every video made, its style, titles, thumbnails and stats.
- `engine/`: lib (drawing + timeline), tts, render, mix, srt, finish, thumbkit.
- `episodes/NNN-slug/`: one folder per video (script.py, scenes.py, thumbs.py).

Setup: `bash setup.sh`. Example: `EP=episodes/001-how-gps-works python3 engine/render.py timeline`.
