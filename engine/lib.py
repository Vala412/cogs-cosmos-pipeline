"""Cogs & Cosmos drawing + timing helpers (skia-python).
Env: EP=<episode dir> (holds script.py, scenes.py, audio/, out/), FORMAT=long (1920x1080) | short (1080x1920)."""
import math, random, json, os
import skia

FPS = 30
ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)
FONTS = os.path.join(ROOT, "fonts")
_ep = os.environ.get("EP", os.getcwd())
EP = os.path.abspath(_ep if os.path.isabs(_ep) or os.path.isdir(_ep) else os.path.join(ROOT, _ep))
FORMAT = os.environ.get("FORMAT", "long")
W, H = (1080, 1920) if FORMAT == "short" else (1920, 1080)
HERE = EP  # outputs (audio/, out/) live in the episode folder

NAVY = "#0B1026"; NAVY2 = "#141C3F"; NAVY3 = "#1E2856"
AMBER = "#F5A524"; TEAL = "#2DD4BF"; CREAM = "#F7F3E8"; MIST = "#B4BED8"
BLUE = "#4C9BFF"; RED = "#FF6B5E"; DIM = "#5B6690"

TF = {
    "head": skia.Typeface.MakeFromFile(f"{FONTS}/SpaceGrotesk-700.ttf"),
    "head5": skia.Typeface.MakeFromFile(f"{FONTS}/SpaceGrotesk-500.ttf"),
    "body": skia.Typeface.MakeFromFile(f"{FONTS}/Inter-Medium.otf"),
    "bodyb": skia.Typeface.MakeFromFile(f"{FONTS}/Inter-SemiBold.otf"),
    "mono": skia.Typeface.MakeFromFile(f"{FONTS}/JetBrainsMono-500.ttf"),
    "monofb": skia.Typeface.MakeFromFile(f"{FONTS}/DejaVuSansMono.ttf"),
}
FALLBACK = {"head": "bodyb", "head5": "body", "mono": "monofb", "body": "body", "bodyb": "bodyb", "monofb": "monofb"}

def runs(s, tf):
    """Split text into runs drawn with the main typeface or its fallback for missing glyphs."""
    out = []; main = TF[tf]; fb = FALLBACK[tf]
    for ch in s:
        use = tf if main.unicharToGlyph(ord(ch)) != 0 or ch == " " else fb
        if out and out[-1][0] == use: out[-1][1] += ch
        else: out.append([use, ch])
    return out


# ---------- maths ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def eo(x):  # ease out cubic
    x = clamp(x); return 1 - (1 - x) ** 3

def eio(x):  # ease in-out
    x = clamp(x); return 3 * x * x - 2 * x * x * x

def lerp(a, b, x):
    return a + (b - a) * x

def back(x):  # ease out back (slight overshoot)
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------- colour / paint ----------
def col(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color4f(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, clamp(a))

def paint(c=CREAM, a=1.0, stroke=None, cap="round", blur=None, dash=None, phase=0.0, join=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, phase))
    return p


# ---------- text ----------
_fonts = {}
def font(tf, size):
    k = (tf, round(size, 1))
    if k not in _fonts:
        f = skia.Font(TF[tf], size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
        _fonts[k] = f
    return _fonts[k]

def tw(s, size, tf="head"):
    return sum(font(t, size).measureText(r) for t, r in runs(s, tf))

def text(c, s, x, y, size, color=CREAM, tf="head", align="c", a=1.0):
    if not s or a <= 0.003:
        return 0
    rs = runs(s, tf); w = sum(font(t, size).measureText(r) for t, r in rs)
    if align == "c": x -= w / 2
    elif align == "r": x -= w
    p = paint(color, a)
    for t, r in rs:
        f = font(t, size); c.drawString(r, x, y, f, p); x += f.measureText(r)
    return w

def text_rise(c, s, x, y, size, prog, color=CREAM, tf="head", align="c", rise=24, a=1.0):
    """Fade + rise in."""
    p = eo(prog)
    text(c, s, x, y + (1 - p) * rise, size, color, tf, align, a=p * a)

def typewriter(c, s, x, y, size, prog, color=CREAM, tf="mono", align="l", cursor=True, t=0, a=1.0):
    n = int(len(s) * clamp(prog))
    shown = s[:n]
    w = text(c, shown, x, y, size, color, tf, align, a)
    if cursor and prog < 1.05 and (int(t * 2.5) % 2 == 0 or prog < 1):
        c.drawRect(skia.Rect.MakeXYWH(x + w + 4, y - size * 0.8, size * 0.5, size * 0.95), paint(color, 0.85 * a))

def pill(c, s, x, y, size, fg=NAVY, bg=AMBER, a=1.0, tf="bodyb", pad=18, align="c"):
    w = tw(s, size, tf) + pad * 2; h = size * 1.7
    if align == "c": x0 = x - w / 2
    elif align == "r": x0 = x - w
    else: x0 = x
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y - h / 2, w, h), h / 2, h / 2)
    c.drawRRect(r, paint(bg, a))
    text(c, s, x0 + w / 2, y + size * 0.36, size, fg, tf, "c", a)
    return w


# ---------- shapes ----------
def ring(c, x, y, r, color=TEAL, a=1.0, w=3, dash=None, phase=0):
    c.drawCircle(x, y, r, paint(color, a, stroke=w, dash=dash, phase=phase))

def line(c, x1, y1, x2, y2, color=CREAM, a=1.0, w=3, dash=None, phase=0):
    c.drawLine(x1, y1, x2, y2, paint(color, a, stroke=w, dash=dash, phase=phase))

def arrow(c, x1, y1, x2, y2, color=CREAM, a=1.0, w=4, head=18):
    line(c, x1, y1, x2, y2, color, a, w)
    ang = math.atan2(y2 - y1, x2 - x1)
    p = skia.Path(); p.moveTo(x2, y2)
    p.lineTo(x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45))
    p.lineTo(x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45)); p.close()
    c.drawPath(p, paint(color, a))

def rrect(c, x, y, w, h, r, color, a=1.0, stroke=None):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint(color, a, stroke=stroke))

def glow_dot(c, x, y, r, color=TEAL, a=1.0):
    c.drawCircle(x, y, r * 2.6, paint(color, 0.25 * a, blur=r * 1.6))
    c.drawCircle(x, y, r, paint(color, a))

def pulse(c, x, y, t, period=1.6, rmax=60, color=TEAL, a=1.0, w=3, n=2):
    for k in range(n):
        ph = ((t / period) + k / n) % 1.0
        ring(c, x, y, 6 + ph * rmax, color, a * (1 - ph) * 0.9, w)

def bg(c, color=NAVY):
    c.clear(col(color))

def vignette(c, a=0.55):
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.72,
                                        [col(NAVY, 0), col("#05081A", a)], [0.55, 1.0])
    p = skia.Paint(Shader=sh); c.drawRect(skia.Rect.MakeWH(W, H), p)


class Stars:
    def __init__(self, n=220, seed=1, area=(W, H)):
        rng = random.Random(seed)
        self.s = [(rng.random() * area[0], rng.random() * area[1], rng.choice([0.9, 1.2, 1.5, 2.0, 2.6]),
                   rng.random() * 6.283, rng.uniform(0.25, 0.9)) for _ in range(n)]

    def draw(self, c, t, drift=(0, 0), a=1.0, color=CREAM):
        for x, y, r, ph, al in self.s:
            xx = (x + drift[0] * t) % W; yy = (y + drift[1] * t) % H
            k = 0.72 + 0.28 * math.sin(t * 1.4 + ph)
            c.drawCircle(xx, yy, r, paint(color, al * k * a))


def earth(c, cx, cy, r, rot=0.0, a=1.0, glow=True, cities=True):
    if glow:
        c.drawCircle(cx, cy, r + 4, paint(TEAL, 0.45 * a, stroke=r * 0.05 + 4, blur=r * 0.06 + 8))
    sh = skia.GradientShader.MakeRadial(skia.Point(cx - r * 0.38, cy - r * 0.42), r * 1.55,
                                        [col("#2F63B5", a), col("#163272", a), col("#0B1838", a)], [0.0, 0.55, 1.0])
    c.drawCircle(cx, cy, r, skia.Paint(AntiAlias=True, Shader=sh))
    c.save()
    pth = skia.Path(); pth.addCircle(cx, cy, r); c.clipPath(pth, doAntiAlias=True)
    gp = paint(TEAL, 0.16 * a, stroke=max(1.2, r * 0.006))
    for lat in range(-60, 61, 30):
        y = cy - r * math.sin(math.radians(lat)); hw = r * math.cos(math.radians(lat))
        c.drawLine(cx - hw, y, cx + hw, y, gp)
    for k in range(12):
        lon = k * math.pi / 6 + rot
        if math.cos(lon) < 0: continue
        pp = skia.Path()
        for j in range(0, 37):
            lat = -math.pi / 2 + j * math.pi / 36
            x = cx + r * math.cos(lat) * math.sin(lon); y = cy - r * math.sin(lat)
            (pp.moveTo if j == 0 else pp.lineTo)(x, y)
        c.drawPath(pp, gp)
    if cities:
        rng = random.Random(7)
        for _ in range(60):
            lat = rng.uniform(-0.9, 1.1); lon = rng.uniform(0, 6.283) + rot
            if math.cos(lon) <= 0.05: continue
            x = cx + r * math.cos(lat) * math.sin(lon); y = cy - r * math.sin(lat)
            c.drawCircle(x, y, max(1.2, r * 0.006), paint(AMBER, 0.55 * a * math.cos(lon)))
    # terminator shading
    sh2 = skia.GradientShader.MakeLinear([skia.Point(cx - r, cy), skia.Point(cx + r, cy)],
                                         [col("#000000", 0), col("#000000", 0.0), col("#000000", 0.35 * a)], [0, 0.55, 1])
    c.drawCircle(cx, cy, r, skia.Paint(AntiAlias=True, Shader=sh2))
    c.restore()


def satellite(c, x, y, s=1.0, ang=0.0, a=1.0, body=AMBER, panel=TEAL):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-24, -3, 24, 3), paint(MIST, a))
    for x0 in (-82, 26):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, -15, 56, 30), 3, 3), paint(panel, a))
        for k in range(1, 4):
            c.drawLine(x0 + k * 14, -15, x0 + k * 14, 15, paint(NAVY, a * 0.8, stroke=2))
        c.drawLine(x0, 0, x0 + 56, 0, paint(NAVY, a * 0.8, stroke=2))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-17, -23, 34, 46), 7, 7), paint(body, a))
    c.drawCircle(0, 0, 7, paint(NAVY, a))
    c.drawLine(0, 23, 0, 33, paint(MIST, a, stroke=3)); c.drawCircle(0, 35, 4, paint(MIST, a))
    c.restore()


def orbit_ellipse(c, cx, cy, rx, ry, ang_deg, color=CREAM, a=0.25, w=2, dash=None, phase=0):
    c.save(); c.translate(cx, cy); c.rotate(ang_deg)
    c.drawOval(skia.Rect.MakeLTRB(-rx, -ry, rx, ry), paint(color, a, stroke=w, dash=dash, phase=phase))
    c.restore()

def orbit_point(cx, cy, rx, ry, ang_deg, theta):
    x = rx * math.cos(theta); y = ry * math.sin(theta)
    A = math.radians(ang_deg)
    return cx + x * math.cos(A) - y * math.sin(A), cy + x * math.sin(A) + y * math.cos(A), math.sin(theta)


def map_screen(c, x, y, w, h, off=(0, 0), a=1.0, seed=3):
    """Dark-theme street map filling a rect (caller clips)."""
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint("#16213F", a))
    rng = random.Random(seed)
    ox, oy = off
    # blocks
    step = 90
    for gx in range(-2, int(w / step) + 3):
        for gy in range(-2, int(h / step) + 3):
            bx = x + gx * step + (ox % step); by = y + gy * step + (oy % step)
            if rng.random() < 0.18:
                c.drawRect(skia.Rect.MakeXYWH(bx + 10, by + 10, step - 20, step - 20), paint("#1F6B5A", 0.55 * a))
            else:
                c.drawRect(skia.Rect.MakeXYWH(bx + 9, by + 9, step - 18, step - 18), paint("#1C2A52", a))
    # main road
    c.drawLine(x - 50, y + h * 0.62 + oy * 0.0, x + w + 50, y + h * 0.42, paint(AMBER, 0.55 * a, stroke=14))
    c.drawLine(x - 50, y + h * 0.62, x + w + 50, y + h * 0.42, paint("#FFD38A", 0.5 * a, stroke=3, dash=[18, 14]))


def blue_dot(c, x, y, t, acc=50, a=1.0):
    c.drawCircle(x, y, acc, paint(BLUE, 0.16 * a))
    c.drawCircle(x, y, acc, paint(BLUE, 0.45 * a, stroke=2))
    pulse(c, x, y, t, 1.8, 46, BLUE, a, 3, 2)
    c.drawCircle(x, y, 17, paint("#FFFFFF", a))
    c.drawCircle(x, y, 12, paint(BLUE, a))


def phone(c, cx, cy, s=1.0, t=0.0, dot=(0.5, 0.55), acc=50, a=1.0, off=(0, 0), draw_dot=True):
    w, h = 360 * s, 720 * s
    x, y = cx - w / 2, cy - h / 2
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 6, y - 6, w + 12, h + 12), 52 * s, 52 * s), paint("#000000", 0.35 * a, blur=30))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 48 * s, 48 * s), paint("#0A0E22", a))
    c.save()
    inner = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 14 * s, y + 14 * s, w - 28 * s, h - 28 * s), 36 * s, 36 * s)
    c.clipRRect(inner, doAntiAlias=True)
    map_screen(c, x, y, w, h, off, a)
    if draw_dot:
        blue_dot(c, x + w * dot[0], y + h * dot[1], t, acc * s, a)
    c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 48 * s, 48 * s), paint(CREAM, 0.9 * a, stroke=6 * s))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - 50 * s, y + 24 * s, 100 * s, 22 * s), 11 * s, 11 * s), paint("#0A0E22", a))
    return x, y, w, h


def gear_path(cx, cy, n, r_root, r_tip, hole, tooth_frac=0.52, taper=0.28):
    step = 2 * math.pi / n; half = step * tooth_frac / 2; tip_half = half * (1 - taper)
    p = skia.Path(); first = True
    for i in range(n):
        a0 = i * step - math.pi / 2
        for ang, r in [(a0 - half, r_root), (a0 - tip_half, r_tip), (a0 + tip_half, r_tip), (a0 + half, r_root)]:
            X, Y = cx + r * math.cos(ang), cy + r * math.sin(ang)
            if first: p.moveTo(X, Y); first = False
            else: p.lineTo(X, Y)
        nxt = (i + 1) * step - math.pi / 2 - half
        for j in range(1, 9):
            ang = a0 + half + (nxt - (a0 + half)) * j / 8
            p.lineTo(cx + r_root * math.cos(ang), cy + r_root * math.sin(ang))
    p.close()
    p.addCircle(cx, cy, hole, skia.PathDirection.kCCW)
    p.setFillType(skia.PathFillType.kEvenOdd)
    return p


def logo(c, cx, cy, size, a=1.0, spin=0.0):
    """Cogs & Cosmos mark: brass cog, cream planet, teal orbit ring. size = full width."""
    s = size / 400.0
    c.save(); c.translate(cx, cy); c.scale(s, s)
    c.save(); c.rotate(spin)
    c.drawPath(gear_path(0, 0, 10, 150, 180, 96), paint(AMBER, a))
    c.restore()
    def ring_half(front):
        c.save(); c.rotate(-18)
        rect = skia.Rect.MakeLTRB(-200, -52, 200, 52)
        start, sweep = (0, 180) if front else (180, 180)
        pth = skia.Path(); pth.addArc(rect, start, sweep)
        c.drawPath(pth, paint(NAVY, a, stroke=30)); c.drawPath(pth, paint(TEAL, a, stroke=14))
        if front: c.drawCircle(150 * math.cos(math.radians(43)), 38 * 1.0, 13, paint(CREAM, a))
        c.restore()
    ring_half(False)
    c.drawCircle(0, 0, 66, paint(CREAM, a))
    pth = skia.Path(); pth.addCircle(0, 0, 66)
    c.save(); c.clipPath(pth, doAntiAlias=True); c.drawCircle(40, 0, 60, paint("#E4DDCB", a)); c.restore()
    ring_half(True)
    c.restore()


def hud_corners(c, a=1.0, color=TEAL, m=48, L=60):
    for (x, y, dx, dy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        line(c, x, y, x + dx * L, y, color, a, 3); line(c, x, y, x, y + dy * L, color, a, 3)


def clock_face(c, cx, cy, r, t, color=CREAM, a=1.0, speed=1.0, label=None, hand=AMBER):
    ring(c, cx, cy, r, color, a, 5)
    for k in range(12):
        ang = k * math.pi / 6
        c.drawLine(cx + (r - 14) * math.sin(ang), cy - (r - 14) * math.cos(ang), cx + (r - 4) * math.sin(ang), cy - (r - 4) * math.cos(ang), paint(color, a * 0.7, stroke=3))
    ang = t * speed * 2 * math.pi
    c.drawLine(cx, cy, cx + (r - 22) * math.sin(ang), cy - (r - 22) * math.cos(ang), paint(hand, a, stroke=6))
    c.drawCircle(cx, cy, 7, paint(hand, a))
    if label: text(c, label, cx, cy + r + 46, 30, color, "body", "c", a)


# ---------- timeline ----------
def build_timeline(lead=0.6):
    import importlib.util
    spec = importlib.util.spec_from_file_location("ep_script", os.path.join(EP, "script.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    LINES = mod.LINES
    meta_path = f"{HERE}/audio/lines.json"
    durs = {}
    if os.path.exists(meta_path):
        for m in json.load(open(meta_path)): durs[m["i"]] = m["dur"]
    t = lead; items = []
    for i, (scene, beat, say, cap, pause) in enumerate(LINES):
        d = durs.get(i, len(say.split()) / 2.65 if say else 0.0)
        items.append({"i": i, "scene": scene, "beat": beat, "start": t, "end": t + d, "say": say, "cap": cap or say})
        t = t + d + pause
    total = t
    scenes = []
    for it in items:
        if not scenes or scenes[-1]["key"] != it["scene"]:
            scenes.append({"key": it["scene"], "start": it["start"], "beats": {}})
        scenes[-1]["beats"][it["beat"]] = (it["start"], it["end"])
    scenes[0]["start"] = 0.0
    for k, sc in enumerate(scenes):
        sc["end"] = scenes[k + 1]["start"] if k + 1 < len(scenes) else total
        sc["beats"] = {b: (s - sc["start"], e - sc["start"]) for b, (s, e) in sc["beats"].items()}
    return items, scenes, total
