"""Write English SRT captions from the timeline (each line split into ≤2-line cues timed by length)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import build_timeline, EP

MAXC = 84; LINE = 42

def chunks(text):
    parts = re.split(r'(?<=[.!?:])\s+|(?<=,)\s+(?=\S)', text)
    out, cur = [], ""
    for p in parts:
        if not cur: cur = p
        elif len(cur) + 1 + len(p) <= MAXC: cur += " " + p
        else: out.append(cur); cur = p
    if cur: out.append(cur)
    fin = []
    for c in out:
        while len(c) > MAXC:
            cut = c.rfind(" ", 0, MAXC); fin.append(c[:cut]); c = c[cut + 1:]
        fin.append(c)
    return fin

def wrap(c):
    if len(c) <= LINE: return c
    mid = len(c) // 2
    l = c.rfind(" ", 0, mid + 6); r = c.find(" ", mid - 6)
    cut = l if (r == -1 or abs(l - mid) <= abs(r - mid)) else r
    return c[:cut] + "\n" + c[cut + 1:]

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

items, scenes, total = build_timeline()
cues = []
for it in items:
    if not it["say"]: continue
    cs = chunks(it["cap"]); n = sum(len(c) for c in cs); t = it["start"]; d = it["end"] - it["start"]
    for c in cs:
        dd = d * len(c) / n; cues.append((t, t + dd, wrap(c))); t += dd
with open(sys.argv[1] if len(sys.argv) > 1 else f"{EP}/out/captions_en.srt", "w") as f:
    for k, (a, b, c) in enumerate(cues, 1):
        f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{c}\n\n")
print(len(cues), "cues")
