"""Curiosity-first versions of the three thumbnails: no numbers, short open-loop headlines."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "engine"))
from thumbkit import *

def note(c, s, x, y, size, color=INK, rot=0.0, paper=False, align="l"):
    c.save(); c.translate(x, y); c.rotate(rot)
    if paper:
        f = fnt("marker", size); w = f.measureText(s); pad = 22
        x0 = -w / 2 - pad if align == "c" else -pad
        c.drawRect(skia.Rect.MakeXYWH(x0 + 10, -size - 4, w + 2 * pad, size * 1.55), paint("#000000", 0.25))
        c.drawRect(skia.Rect.MakeXYWH(x0, -size - 14, w + 2 * pad, size * 1.55), paint(CREAM))
    txt(c, s, 0, 0, size, color, "marker", align)
    c.restore()

# ---------- 1. map: EINSTEIN STOPS THIS ----------
def t_map2(path):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    city_map(c, 0, 0, W, H, sea=True)
    hx, hy = 560, 830
    house(c, hx, hy - 40, 1.25)
    blue_dot(c, hx + 120, hy + 30, 26)
    px, py = 1560, 690
    pts = bezier_pts((hx + 150, hy + 10), (1100, 560), (px - 30, py - 40), 30)
    for i in range(0, len(pts) - 1, 2):
        sketch(c, [pts[i], pts[i + 1]], INK, 9, seed=i, passes=1, jit=1.2)
    map_pin(c, px, py, 112, RED)
    # headline
    sticker(c, "EINSTEIN", 60, 60, 220, INK, AMBER, "anton", rot=-4)
    sticker(c, "STOPS THIS", 80, 300, 160, CREAM, INK, "anton", rot=-4)
    sketch_arrow(c, [(860, 330), (1060, 260), (1260, 300), (1400, 400)], RUST, 12, seed=8, head=40)
    # story notes
    note(c, "GPS thinks you're here", 1240, 830, 52, INK, rot=-3, paper=True)
    note(c, "you're actually here", 90, 1010, 54, INK)
    sketch_arrow(c, [(430, 960), (470, 920), (500, 880)], INK, 8, seed=5, head=30)
    finish(surf, path)

# ---------- 2. poster: TIME IS FASTER UP THERE ----------
def t_poster2(path):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(PAPER))
    c.save(); c.translate(1420, 520)
    for i in range(18):
        p = skia.Path(); a0 = math.radians(i * 20); a1 = math.radians(i * 20 + 10)
        p.moveTo(0, 0); p.lineTo(1600 * math.cos(a0), 1600 * math.sin(a0)); p.lineTo(1600 * math.cos(a1), 1600 * math.sin(a1)); p.close()
        c.drawPath(p, paint("#E9DCBC"))
    c.restore()
    halftone_earth(c, 1420, 1250, 640)
    orb = skia.Path(); orb.addOval(skia.Rect.MakeLTRB(760, 300, 2080, 900))
    c.drawPath(orb, paint(INK, 0.8, stroke=5, dash=[22, 16]))
    flat_sat(c, 1200, 360, 1.4, -12)
    clock(c, 1590, 380, 175)
    for k, (a0, sw) in enumerate([(-60, 40), (130, 40), (200, 30)]):
        arc = skia.Path(); rr = 215 + k * 6
        arc.addArc(skia.Rect.MakeLTRB(1590 - rr, 380 - rr, 1590 + rr, 380 + rr), a0, sw)
        c.drawPath(arc, paint(RUST, 1, stroke=12))
    note(c, "ticking ahead!", 1290, 140, 64, RUST, rot=-3)
    sketch_arrow(c, [(1745, 120), (1790, 150), (1800, 200)], RUST, 8, seed=3, head=28)
    txt(c, "TIME", 80, 300, 250, INK, "anton")
    txt(c, "IS FASTER", 80, 560, 230, RUST, "anton")
    txt(c, "UP THERE", 80, 820, 230, INK, "anton")
    c.drawRect(skia.Rect.MakeXYWH(26, 26, W - 52, H - 52), paint(INK, 1, stroke=10))
    finish(surf, path, grain=8.0)

# ---------- 3. phone: SPACE IS TALKING TO YOUR PHONE ----------
def t_phone2(path):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(AMBER))
    for k in range(9):
        c.drawCircle(1400, 620, 140 + k * 130, paint("#E8961A", 0.55, stroke=46))
    pw, ph = 480, 960
    c.save(); c.translate(1400, 640); c.rotate(8)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2 + 28, -ph / 2 + 28, pw, ph), 66, 66), paint(INK, 0.35))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), 66, 66), paint(INK))
    scr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pw / 2 + 24, -ph / 2 + 24, pw - 48, ph - 48), 46, 46)
    c.save(); c.clipRRect(scr, doAntiAlias=True)
    city_map(c, -pw / 2, -ph / 2, pw, ph, sea=False, seed=11, ang=-20)
    blue_dot(c, 0, 60, 30)
    c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-64, -ph / 2 + 40, 128, 32), 16, 16), paint(INK))
    c.restore()
    # satellite top right, signal arcs heading to the phone
    sx, sy = 1010, 120
    flat_sat(c, sx, sy, 0.95, -20)
    for k in range(3):
        rr = 120 + k * 60
        pts = [(sx + rr * math.cos(math.radians(a)), sy + rr * math.sin(math.radians(a))) for a in range(10, 71, 10)]
        sketch(c, pts, INK, 10, seed=20 + k, passes=1, jit=1.5)
    note(c, "it only listens!", 1400, 1040, 58, RUST, rot=-4, paper=True, align="c")
    txt(c, "SPACE IS", 80, 280, 190, INK, "anton")
    sticker(c, "TALKING TO", 62, 330, 190, AMBER, INK, "anton", rot=-3)
    txt(c, "YOUR PHONE", 80, 730, 190, INK, "anton")
    finish(surf, path)

if __name__ == "__main__":
    for k in sys.argv[1:] or ["map", "poster", "phone"]:
        {"map": t_map2, "poster": t_poster2, "phone": t_phone2}[k](f"{HERE}/out/thumb4_{k}.png"); print(k)
