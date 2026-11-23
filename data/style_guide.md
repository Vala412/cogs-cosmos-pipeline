# Cogs & Cosmos — style guide and standing rules

English science / "how things work" channel with a **sci-fi feel**. Faceless, fully animated, AI narration.

## Rules from the owner (follow every time)
- **Outro:** a short like / subscribe / hit-the-bell call to action, then the logo and "Keep exploring." No "next week" teaser for a specific video. No end-screen background section while the channel has few videos.
- **Thumbnails:** must not look AI-generated: no glow, no bloom, no glossy gradients, no purple/teal nebula. Use flat colours, dark outlines, hard offset shadows, light print grain, bold poster fonts (Anton / Archivo Black), and a hand-lettered marker note (Permanent Marker). See `engine/thumbkit.py`.
- **Thumbnail text sparks curiosity, never maths.** 2–5 words, no numbers or units (no "11 KM", "+38 µs"). Examples that worked for the owner: "EINSTEIN STOPS THIS", "SPACE IS TALKING TO YOUR PHONE", "TIME IS FASTER UP THERE".
- **Make 3 thumbnails per video** (different concepts/styles) for YouTube's A/B test, plus **3 titles** that pair with them. Title and thumbnail say different things; title ≤ 60 characters; every claim must be delivered by the video.
- **Each video uses a visual style different from the previous ones** (see `data/videos.json` "style"). Research what competitors and top science channels do, then make an original take. Never copy anyone's scripts, characters or artwork.
- **Owner approves before anything is uploaded.**

## Brand
- Colours: navy `#0B1026` (bg), navy2 `#141C3F`, navy3 `#1E2856`, amber `#F5A524`, teal `#2DD4BF`, cream `#F7F3E8`, mist `#B4BED8`, blue `#4C9BFF`, red `#FF6B5E`. Thumbnail ink `#14183A`, paper `#F2E8D2`, rust `#E4572E`.
- Fonts (in `fonts/`): Space Grotesk 700 (headings), Inter (body), JetBrains Mono (data/HUD), Anton / Archivo Black / Bebas Neue (thumbnails), Permanent Marker (hand notes). `lib.text()` falls back to Inter/DejaVu for symbols the heading font lacks (≈ → × µ).
- Logo: `lib.logo()` (brass cog, cream planet, teal ring).
- Voice: Kokoro `af_heart`, speed 0.96 (Apache-2.0). Spell numbers out in the spoken text; captions use digits. Spell tricky names phonetically in spoken text only.
- Music/SFX: original, synthesized in `engine/mix.py` (moods: calm, tense, drone, bright). Mix lands at about −14 LUFS.

## Formats
- **Short** (daily): 1080×1920 (`FORMAT=short`), 40–60 s. Hook in the first 2 seconds (a question or a strange visual), one idea, a payoff, then a 3–4 s like/subscribe/bell line. Big burnt-in captions are fine for Shorts. Must be ≤ 3.6 MB to upload through Chrome (`finish.py --max-mb 3.6`).
- **Long** (Tuesdays): 1920×1080, 6–8 min. Cold open/hook ≤ 30 s, chapter tags on screen, 4–6 chapters, a twist in the second half, a callback to the opening, then the outro.

## Upload settings
- Audience: not made for kids. Category: Education (type: Concept overview), as on video 1. Language: English. AI use question: answer honestly against the listed uses (fake real person, altered real footage, realistic scene that never happened, AI music as the focus). Our drawn animation + synthesized narrator + synthesized music match none of them, so "No", unless a video adds realistic AI imagery. Captions: upload the episode's `.srt`. Automatic dubbing on (Hindi expressive). Playlist: "Tech Decoded" (long videos).
- Description: 1–2 hook sentences, chapters (long videos only, first at 00:00, each ≥ 10 s), sources list, the line "All animation and music are original, made for Cogs & Cosmos. Narration uses an AI voice.", subscribe link `https://www.youtube.com/@CogsAndCosmos?sub_confirmation=1`, 3 hashtags (Shorts include #Shorts).
- Tags: ≤ 500 characters, main search phrases first, include one Hindi search phrase.
- Publish time: **7:30 PM IST** (scheduled publish).
