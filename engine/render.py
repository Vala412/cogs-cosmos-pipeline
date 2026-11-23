"""Render an episode. Run with EP=<episode dir> [FORMAT=short]. Usage:
  python3 render.py stills 12.5 40 ...     # PNGs at global times (seconds)
  python3 render.py scenes                  # encode every scene to out/scenes/NN_key.mp4
  python3 render.py scene KEY               # encode one scene
"""
import sys, os, subprocess, json, time
import numpy as np
import skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
sys.path.insert(0, EP)
from scenes import SCENES

items, scenes, total = build_timeline()
os.makedirs(f"{HERE}/out/scenes", exist_ok=True)
os.makedirs(f"{HERE}/out/stills", exist_ok=True)

arr = np.zeros((H, W, 4), dtype=np.uint8)
surface = skia.Surface(arr)

def draw(gt):
    for sc in scenes:
        if sc["start"] <= gt < sc["end"] or sc is scenes[-1]:
            break
    t = gt - sc["start"]; D = sc["end"] - sc["start"]
    with surface as c:
        c.save()
        SCENES[sc["key"]](c, t, sc["beats"], D)
        c.restore()
        f = max(clamp(1 - t / 0.35), clamp(1 - (D - t) / 0.35)) if sc["key"] not in ("end",) else clamp(1 - t / 0.35)
        if f > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, f))
    return sc

def stills(times):
    for gt in times:
        sc = draw(gt)
        img = surface.makeImageSnapshot()
        p = f"{HERE}/out/stills/t{gt:07.2f}_{sc['key']}.png"
        img.save(p, skia.kPNG); print(p)

def encode_scene(k):
    sc = scenes[k]
    f0 = round(sc["start"] * FPS); f1 = round(sc["end"] * FPS)
    out = f"{HERE}/out/scenes/{k:02d}_{sc['key']}.mp4"; tmp = out[:-4] + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        draw(f / FPS)
        pr.stdin.write(arr.tobytes())
    pr.stdin.close(); rc = pr.wait()
    if rc == 0: os.replace(tmp, out)
    print(f"scene {k:02d} {sc['key']}: {f1 - f0} frames in {time.time() - t0:.1f}s rc={rc}", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        stills([float(x) for x in sys.argv[2:]])
    elif mode == "timeline":
        for sc in scenes:
            print(f"{sc['key']:6s} {sc['start']:7.2f} -> {sc['end']:7.2f}  ({sc['end'] - sc['start']:.1f}s)  beats: " + ", ".join(f"{b}@{s:.1f}" for b, (s, e) in sc['beats'].items()))
        print("total", round(total, 2))
    elif mode == "scenes":
        for k in range(len(scenes)): encode_scene(k)
    elif mode == "scene":
        for k, sc in enumerate(scenes):
            if sc["key"] == sys.argv[2]: encode_scene(k)
