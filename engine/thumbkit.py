"""Hand-designed-looking thumbnails: flat colours, no glow, hard shadows, print grain.
Three directions:  map  (dot lost at sea), poster (retro science print), phone (bold flat phone)."""
import os, sys, math, random
import numpy as np, skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import W, H, NAVY, AMBER, TEAL, CREAM, MIST, BLUE, RED, col, paint, clamp
from PIL import Image

from lib import FONTS, EP
HERE = EP
F = {k: skia.Typeface.MakeFromFile(f"{FONTS}/{v}.ttf") for k, v in
     {"anton": "anton", "archivo": "archivo-black", "marker": "permanent-marker", "grot": "SpaceGrotesk-700"}.items()}
INK = "#14183A"; PAPER = "#F2E8D2"; RUST = "#E4572E"

def fnt(k, s): return skia.Font(F[k], s)

def txt(c, s, x, y, size, color, face="anton", align="l", a=1.0):
    f = fnt(face, size); w = f.measureText(s)
    if align == "c": x -= w / 2
    elif align == "r": x -= w
    c.drawString(s, x, y, f, paint(color, a)); return w

def sticker(c, s, x, y, size, fg, bgc, face="anton", rot=0.0, padx=34, pady=18, shadow=True):
    """Text on a solid block, slightly rotated, hard offset shadow (print style)."""
    f = fnt(face, size); w = f.measureText(s)
    m = f.getMetrics(); asc, desc = -m.fAscent, m.fDescent
    capH = size * 0.74 if face == "anton" else size * 0.72
    bw, bh = w + 2 * padx, capH + 2 * pady
    c.save(); c.translate(x, y); c.rotate(rot)
    if shadow:
        c.drawRect(skia.Rect.MakeXYWH(12, 12, bw, bh), paint("#000000", 0.28))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, bw, bh), paint(bgc))
    c.drawString(s, padx, pady + capH, f, paint(fg))
    c.restore()
    return bw, bh

def sketch(c, pts, color, width, seed=1, a=1.0, passes=2, jit=3.0):
    """Marker-like hand-drawn polyline through pts (smoothed, slightly wobbly)."""
    rng = random.Random(seed)
    for k in range(passes):
        p = skia.Path()
        q = [(x + rng.uniform(-jit, jit), y + rng.uniform(-jit, jit)) for x, y in pts]
        p.moveTo(*q[0])
        for i in range(1, len(q) - 1):
            mx, my = (q[i][0] + q[i + 1][0]) / 2, (q[i][1] + q[i + 1][1]) / 2
            p.quadTo(q[i][0], q[i][1], mx, my)
        p.lineTo(*q[-1])
        c.drawPath(p, paint(color, a * (0.95 if k == 0 else 0.55), stroke=width * (1 if k == 0 else 0.7)))

def sketch_arrow(c, pts, color, width, seed=1, head=34):
    sketch(c, pts, color, width, seed)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (2.55, -2.55):
        sketch(c, [(x2, y2), (x2 + head * math.cos(ang + s), y2 + head * math.sin(ang + s))], color, width, seed + 7, passes=1, jit=1.5)

def bezier_pts(p0, p1, p2, n=18):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / (n - 1) for i in range(n)]]

# ---------------- flat city map ----------------
LAND = "#EFE3C8"; STREET = "#FFFDF6"; BLOCK = "#E5D3AE"; PARK = "#B7D58F"; WATER = "#86CFD6"; WATER_D = "#5DB3BE"; HWY = "#F6C94E"

def city_map(c, x0, y0, w, h, sea=True, seed=4, ang=-14):
    rng = random.Random(seed)
    c.save(); c.clipRect(skia.Rect.MakeXYWH(x0, y0, w, h))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), paint(STREET))
    c.save(); c.translate(x0 + w / 2, y0 + h / 2); c.rotate(ang)
    D = int(max(w, h) * 0.9); y = -D
    while y < D:
        bh = rng.choice([110, 130, 150, 170]); x = -D
        while x < D:
            bw = rng.choice([120, 150, 190, 240])
            colr = PARK if rng.random() < 0.07 else BLOCK
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 9, y + 9, bw - 18, bh - 18), 8, 8), paint(colr))
            x += bw
        y += bh
    c.restore()
    # highways
    for (a_, b_, c_) in [((x0 - 50, y0 + h * 0.62), (x0 + w * 0.45, y0 + h * 0.48), (x0 + w + 50, y0 + h * 0.70)),
                         ((x0 + w * 0.30, y0 - 50), (x0 + w * 0.36, y0 + h * 0.5), (x0 + w * 0.22, y0 + h + 50))]:
        p = skia.Path(); p.moveTo(*a_); p.quadTo(*b_, *c_)
        c.drawPath(p, paint("#D9A93A", 1, stroke=34, cap="butt")); c.drawPath(p, paint(HWY, 1, stroke=24, cap="butt"))
    if sea:
        p = skia.Path(); sx = x0 + w * 0.64
        p.moveTo(sx, y0 - 10)
        p.cubicTo(sx - 90, y0 + h * 0.25, sx + 110, y0 + h * 0.45, sx - 30, y0 + h * 0.70)
        p.cubicTo(sx - 120, y0 + h * 0.85, sx + 40, y0 + h * 0.95, sx - 10, y0 + h + 10)
        p.lineTo(x0 + w + 10, y0 + h + 10); p.lineTo(x0 + w + 10, y0 - 10); p.close()
        c.drawPath(p, paint(WATER)); c.drawPath(p, paint(WATER_D, 1, stroke=6))
        # river
        r = skia.Path(); r.moveTo(x0 - 20, y0 + h * 0.18)
        r.cubicTo(x0 + w * 0.2, y0 + h * 0.10, x0 + w * 0.42, y0 + h * 0.32, sx + 10, y0 + h * 0.30)
        c.drawPath(r, paint(WATER_D, 1, stroke=44)); c.drawPath(r, paint(WATER, 1, stroke=36))
        # little wave marks
        rr = random.Random(9)
        for _ in range(16):
            wx = rr.uniform(sx + 120, x0 + w - 40); wy = rr.uniform(y0 + 60, y0 + h - 60)
            sketch(c, [(wx, wy), (wx + 14, wy - 8), (wx + 28, wy), (wx + 42, wy - 8)], WATER_D, 5, seed=int(wx), passes=1, jit=0.8)
    c.restore()

def house(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-40 + 8, -40 + 8, 80, 70), paint("#000000", 0.18))
    c.drawRect(skia.Rect.MakeXYWH(-40, -40, 80, 70), paint(CREAM)); c.drawRect(skia.Rect.MakeXYWH(-40, -40, 80, 70), paint(INK, 1, stroke=6))
    p = skia.Path(); p.moveTo(-56, -36); p.lineTo(0, -86); p.lineTo(56, -36); p.close()
    c.drawPath(p, paint(RUST)); c.drawPath(p, paint(INK, 1, stroke=6, join="round"))
    c.drawRect(skia.Rect.MakeXYWH(-12, -2, 24, 32), paint(INK))
    c.restore()

def blue_dot(c, x, y, r=34):
    c.drawCircle(x, y, r * 2.6, paint(BLUE, 0.22)); c.drawCircle(x, y, r * 2.6, paint(BLUE, 0.6, stroke=3))
    c.drawCircle(x + 5, y + 6, r + 8, paint("#000000", 0.18))
    c.drawCircle(x, y, r + 8, paint("#FFFFFF")); c.drawCircle(x, y, r, paint(BLUE))

def map_pin(c, x, y, R, fill=RED):
    p = skia.Path(); p.moveTo(x, y)
    p.cubicTo(x - 0.55 * R, y - 0.75 * R, x - R, y - 1.05 * R, x - R, y - 1.6 * R)
    p.arcTo(skia.Rect.MakeLTRB(x - R, y - 2.6 * R, x + R, y - 0.6 * R), 180, 180, False)
    p.cubicTo(x + R, y - 1.05 * R, x + 0.55 * R, y - 0.75 * R, x, y); p.close()
    sh = skia.Path(p); m = skia.Matrix(); m.setTranslate(14, 14); sh.transform(m)
    c.drawPath(sh, paint("#000000", 0.22))
    c.drawPath(p, paint(fill)); c.drawPath(p, paint(INK, 1, stroke=7, join="round"))
    c.drawCircle(x, y - 1.6 * R, 0.42 * R, paint(CREAM)); c.drawCircle(x, y - 1.6 * R, 0.42 * R, paint(INK, 1, stroke=6))

def finish(surf, path, grain=7.0):
    arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]
    img = Image.fromarray(arr).resize((1280, 720), Image.LANCZOS)
    a = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(3)
    a += rng.normal(0, grain, (720, 1280, 1)).astype(np.float32)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(path, optimize=True)

# ---------------- 1. dot lost at sea ----------------
def t_map(path):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    city_map(c, 0, 0, W, H, sea=True)
    hx, hy = 560, 830
    house(c, hx, hy - 40, 1.25)
    blue_dot(c, hx + 120, hy + 30, 26)
    px, py = 1560, 640
    # dashed drift route
    pts = bezier_pts((hx + 150, hy + 10), (1100, 520), (px - 30, py - 40), 30)
    for i in range(0, len(pts) - 1, 2):
        sketch(c, [pts[i], pts[i + 1]], INK, 9, seed=i, passes=1, jit=1.2)
    map_pin(c, px, py, 118, RED)
    sticker(c, "11 KM A DAY", 1010, 690, 64, CREAM, INK, "anton", rot=-6, padx=26, pady=14)
    sticker(c, "WITHOUT", 70, 70, 140, CREAM, INK, "anton", rot=-4)
    sticker(c, "EINSTEIN", 60, 255, 220, INK, AMBER, "anton", rot=-4)
    # hand note pointing at the house
    txt(c, "you're here", 150, 1010, 64, INK, "marker")
    sketch_arrow(c, [(430, 960), (470, 920), (500, 880)], INK, 8, seed=5, head=30)
    finish(surf, path)

# ---------------- 2. retro science poster ----------------
def clock(c, x, y, r, t=0.0):
    c.drawCircle(x + 12, y + 12, r, paint("#000000", 0.2))
    c.drawCircle(x, y, r, paint(CREAM)); c.drawCircle(x, y, r, paint(INK, 1, stroke=16))
    for i in range(12):
        a = i * math.pi / 6; r1 = r * (0.78 if i % 3 else 0.70)
        c.drawLine(x + r1 * math.sin(a), y - r1 * math.cos(a), x + r * 0.88 * math.sin(a), y - r * 0.88 * math.cos(a), paint(INK, 1, stroke=7 if i % 3 else 11))
    for ang, ln, wd, colr in [(300, 0.50, 16, INK), (60, 0.72, 10, RUST)]:
        a = math.radians(ang)
        c.drawLine(x, y, x + r * ln * math.sin(a), y - r * ln * math.cos(a), paint(colr, 1, stroke=wd))
    c.drawCircle(x, y, 14, paint(INK))

def halftone_earth(c, cx, cy, R):
    c.drawCircle(cx + 16, cy + 16, R, paint("#000000", 0.15))
    c.drawCircle(cx, cy, R, paint("#2B4C8C"))
    pth = skia.Path(); pth.addCircle(cx, cy, R)
    c.save(); c.clipPath(pth, doAntiAlias=True)
    # simple land blobs
    rng = random.Random(2)
    for _ in range(7):
        bx, by = cx + rng.uniform(-R * 0.8, R * 0.5), cy + rng.uniform(-R * 0.9, -R * 0.2)
        blob = skia.Path(); blob.addOval(skia.Rect.MakeXYWH(bx, by, rng.uniform(120, 300), rng.uniform(70, 160)))
        c.drawPath(blob, paint("#5E8F5A"))
    # halftone shading toward the lower-right
    step = 22
    for gx in range(int(cx - R), int(cx + R), step):
        for gy in range(int(cy - R), int(cy + R), step):
            d = ((gx - (cx - R * 0.5)) + (gy - (cy - R * 0.6))) / (2.2 * R)
            rr = clamp(d) * step * 0.55
            if rr > 1: c.drawCircle(gx, gy, rr, paint(INK, 0.55))
    c.restore()
    c.drawCircle(cx, cy, R, paint(INK, 1, stroke=12))

def flat_sat(c, x, y, s, ang):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-30, -4, 30, 4), paint(INK))
    for x0 in (-110, 34):
        r = skia.Rect.MakeXYWH(x0, -22, 76, 44)
        c.drawRect(r, paint("#3F78B5")); c.drawRect(r, paint(INK, 1, stroke=5))
        for k in range(1, 4): c.drawLine(x0 + k * 19, -22, x0 + k * 19, 22, paint(INK, 1, stroke=3))
        c.drawLine(x0, 0, x0 + 76, 0, paint(INK, 1, stroke=3))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, -34, 52, 68), 8, 8)
    c.drawRRect(r, paint(AMBER)); c.drawRRect(r, paint(INK, 1, stroke=5))
    c.drawLine(0, 34, 0, 52, paint(INK, 1, stroke=5)); c.drawCircle(0, 56, 7, paint(INK))
    c.restore()

def t_poster(path):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(PAPER))
    # sun-ray stripes behind the art
    c.save(); c.translate(1420, 520)
    for i in range(18):
        p = skia.Path(); a0 = math.radians(i * 20); a1 = math.radians(i * 20 + 10)
        p.moveTo(0, 0); p.lineTo(1600 * math.cos(a0), 1600 * math.sin(a0)); p.lineTo(1600 * math.cos(a1), 1600 * math.sin(a1)); p.close()
        c.drawPath(p, paint("#E9DCBC"))
    c.restore()
    halftone_earth(c, 1420, 1250, 640)
    orb = skia.Path(); orb.addOval(skia.Rect.MakeLTRB(760, 300, 2080, 900))
    c.drawPath(orb, paint(INK, 0.8, stroke=5, dash=[22, 16]))
    flat_sat(c, 1160, 360, 1.5, -12)
    clock(c, 1560, 380, 175)
    # speed marks around the clock
    for k, (a0, sw) in enumerate([(-60, 40), (130, 40), (200, 30)]):
        arc = skia.Path(); rr = 215 + k * 6
        arc.addArc(skia.Rect.MakeLTRB(1560 - rr, 380 - rr, 1560 + rr, 380 + rr), a0, sw)
        c.drawPath(arc, paint(RUST, 1, stroke=12))
    txt(c, "+38 millionths", 1350, 690, 54, RUST, "marker")
    txt(c, "of a second a day", 1350, 752, 44, INK, "marker")
    sketch_arrow(c, [(1520, 640), (1545, 600), (1555, 575)], RUST, 8, seed=3, head=28)
    # headline
    txt(c, "GPS", 80, 300, 250, INK, "anton")
    txt(c, "CLOCKS", 80, 560, 250, INK, "anton")
    txt(c, "RUN FAST", 80, 820, 250, RUST, "anton")
    # print border
    c.drawRect(skia.Rect.MakeXYWH(26, 26, W - 52, H - 52), paint(INK, 1, stroke=10))
    finish(surf, path, grain=8.0)

# ---------------- 3. bold phone ----------------
def t_phone(path):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(AMBER))
    for k in range(9):
        c.drawCircle(1420, 560, 140 + k * 130, paint("#E8961A", 0.55, stroke=46))
    # phone
    pw, ph = 520, 1040
    c.save(); c.translate(1420, 560); c.rotate(8)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2 + 28, -ph / 2 + 28, pw, ph), 70, 70), paint(INK, 0.35))
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 70, 70)
    c.drawRRect(body, paint(INK))
    scr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2 + 26, -ph / 2 + 26, pw - 52, ph - 52), 50, 50)
    c.save(); c.clipRRect(scr, doAntiAlias=True)
    city_map(c, -pw / 2, -ph / 2, pw, ph, sea=False, seed=11, ang=-20)
    blue_dot(c, -40, 120, 30)
    c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-70, -ph / 2 + 44, 140, 34), 17, 17), paint(INK))
    c.restore()
    # the dot sliding off the screen, with a marker note
    gx, gy = 1820, 300
    pts = bezier_pts((1420, 650), (1650, 420), (gx - 40, gy + 30), 22)
    for i in range(0, len(pts) - 1, 2):
        sketch(c, [pts[i], pts[i + 1]], INK, 9, seed=i, passes=1, jit=1.0)
    c.drawCircle(gx + 6, gy + 8, 44, paint("#000000", 0.2))
    c.drawCircle(gx, gy, 44, paint(RED)); c.drawCircle(gx, gy, 44, paint(INK, 1, stroke=7))
    c.save(); c.translate(1300, 250); c.rotate(-7)
    c.drawRect(skia.Rect.MakeXYWH(10, 10, 300, 96), paint("#000000", 0.25))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, 300, 96), paint(CREAM))
    txt(c, "drifting!", 150, 70, 60, RUST, "marker", "c")
    c.restore()
    # headline
    txt(c, "YOUR PHONE", 80, 300, 190, INK, "anton")
    txt(c, "NEEDS", 80, 520, 190, INK, "anton")
    sticker(c, "EINSTEIN", 62, 600, 230, AMBER, INK, "anton", rot=-4)
    finish(surf, path)

if __name__ == "__main__":
    which = sys.argv[1:] or ["map", "poster", "phone"]
    for k in which:
        {"map": t_map, "poster": t_poster, "phone": t_phone}[k](f"{HERE}/out/thumb3_{k}.png"); print(k)
