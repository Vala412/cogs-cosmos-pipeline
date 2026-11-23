"""Scene renderers. Each takes (c, t, B, D): canvas, local time, beat windows {beat: (start, end)}, duration."""
import math, random
import skia
from lib import *

STARS = Stars(240, 11)
STARS2 = Stars(160, 29)
MARS_STARS = Stars(120, 5)


def P(t, B, beat, d=0.7, delay=0.0):
    if beat not in B: return 0.0
    return eo((t - B[beat][0] - delay) / d)

def since(t, B, beat):
    return t - B[beat][0] if beat in B else -1

def on(t, B, beat, delay=0.0):
    return beat in B and t >= B[beat][0] + delay

def xfade(t, B, beat, d=0.6, delay=0.0):
    """0 before the beat, rising to 1 over d seconds."""
    return eio((t - B[beat][0] - delay) / d) if beat in B else 0.0

def chapter_tag(c, n, label, a=1.0):
    text(c, f"{n:02d}", 72, 92, 26, AMBER, "mono", "l", a)
    text(c, label.upper(), 122, 92, 26, MIST, "mono", "l", a * 0.9)


# ============================== MARS ==============================
def dune_path(base, amp, freq, phase, seed):
    rng = random.Random(seed); comps = [(rng.uniform(0.5, 1.6) * freq, rng.uniform(0, 6.28), rng.uniform(0.3, 1.0)) for _ in range(4)]
    p = skia.Path(); p.moveTo(-20, H + 20)
    for x in range(-20, W + 41, 20):
        y = base + sum(a * amp * math.sin(x * f / 1000 + ph + phase) for f, ph, a in comps) / 2
        p.lineTo(x, y)
    p.lineTo(W + 40, H + 20); p.close(); return p

def rover(c, x, y, s=1.0, t=0.0, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    body = "#E7DCCB"
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-90, -60, 180, 46), 10, 10), paint(body, a))
    c.drawRect(skia.Rect.MakeXYWH(-80, -72, 120, 12), paint(TEAL, a * 0.9))
    c.drawLine(40, -60, 40, -130, paint(body, a, stroke=7))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(22, -150, 44, 24), 6, 6), paint(body, a))
    c.drawCircle(56, -138, 6, paint(NAVY, a))
    c.drawLine(-60, -60, -75, -112, paint(body, a, stroke=5)); c.drawOval(skia.Rect.MakeXYWH(-100, -132, 50, 22), paint(body, a))
    for wx in (-70, 0, 70):
        c.drawCircle(wx, -6, 20, paint("#2A1A16", a)); c.drawCircle(wx, -6, 8, paint(body, a * 0.8))
    # blinking beacon
    if int(t * 2) % 2 == 0: c.drawCircle(-80, -78, 6, paint(AMBER, a))
    c.restore()

def mars_bg(c, t, night=False):
    top, mid = ("#0A0408", "#2B0F10") if night else ("#14070A", "#4A1C12")
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H * 0.72)], [col(top), col(mid)], [0, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    MARS_STARS.draw(c, t, (2, 0), 0.9 if night else 0.45)
    if not night:
        c.drawCircle(420, 230, 46, paint("#F3D9B1", 0.25, blur=40)); c.drawCircle(420, 230, 20, paint("#F7E7CC", 0.85))
    for base, amp, colr, ph, sp, sd in [(700, 60, "#5E2416", 0, 0.004, 1), (790, 70, "#7A2E17", 1.2, 0.009, 2), (900, 50, "#9C3F1C", 2.1, 0.016, 3)]:
        c.drawPath(dune_path(base, amp, 2.2, ph + t * sp, sd), paint(colr if not night else colr, 1.0 if not night else 0.75))
    if night:
        c.drawRect(skia.Rect.MakeWH(W, H), paint("#05030A", 0.35))

def S_mars(c, t, B, D):
    mars_bg(c, t)
    ry = 786 + 4 * math.sin(t * 2.1)
    rover(c, 1180 + t * 6, ry, 1.0, t)
    hud_corners(c, 0.55)
    if on(t, B, "log1"):
        p = clamp(since(t, B, "log1") / 2.2)
        typewriter(c, "MISSION LOG // DAY 212", 96, 120, 34, p, TEAL, t=t)
        typewriter(c, "MARS · 2140", 96, 168, 28, clamp((since(t, B, "log1") - 2.0) / 1.0), MIST, cursor=False)
        pill(c, "FICTION", W - 96, 118, 24, NAVY, AMBER, P(t, B, "log1", 0.5), align="r")
    if on(t, B, "blank"):
        a = P(t, B, "blank", 0.6)
        x0, y0, w0, h0 = 1180, 260, 600, 360
        rrect(c, x0, y0, w0, h0, 16, NAVY, 0.82 * a); rrect(c, x0, y0, w0, h0, 16, TEAL, 0.7 * a, stroke=2)
        for k in range(1, 6): line(c, x0 + k * w0 / 6, y0 + 50, x0 + k * w0 / 6, y0 + h0 - 20, TEAL, 0.12 * a, 1.5)
        for k in range(1, 4): line(c, x0 + 20, y0 + 50 + k * (h0 - 70) / 4, x0 + w0 - 20, y0 + 50 + k * (h0 - 70) / 4, TEAL, 0.12 * a, 1.5)
        text(c, "ROVER MAP", x0 + 24, y0 + 36, 22, MIST, "mono", "l", a)
        cx, cy = x0 + w0 / 2, y0 + h0 / 2 + 20
        c.save(); c.translate(cx, cy); c.rotate(t * 40)
        ring(c, 0, 0, 46, AMBER, 0.8 * a, 3, dash=[14, 10]); c.restore()
        line(c, cx - 70, cy, cx + 70, cy, AMBER, 0.6 * a, 2); line(c, cx, cy - 70, cx, cy + 70, AMBER, 0.6 * a, 2)
        blink = 0.35 + 0.65 * (int(t * 2.5) % 2)
        text(c, "POSITION: UNKNOWN", cx, y0 + h0 - 26, 26, AMBER, "mono", "c", a * blink)
    if on(t, B, "nogps"):
        a = P(t, B, "nogps", 0.6) * (1 - P(t, B, "howit", 1.0, 1.0))
        sweep = (since(t, B, "nogps") * 50) % 180
        c.save(); c.translate(760, 820)
        pth = skia.Path(); pth.addArc(skia.Rect.MakeLTRB(-700, -620, 700, 620), 180 + sweep, 6)
        c.drawPath(pth, paint(TEAL, 0.6 * a, stroke=6))
        pth2 = skia.Path(); pth2.addArc(skia.Rect.MakeLTRB(-700, -620, 700, 620), 180, 180)
        c.drawPath(pth2, paint(TEAL, 0.25 * a, stroke=2, dash=[10, 14]))
        c.restore()
        text(c, "SATELLITES IN VIEW: 0", 760, 300, 30, TEAL, "mono", "c", a)
    if on(t, B, "trick"):
        a = P(t, B, "trick", 0.8) * (1 - P(t, B, "howit", 1.0, 1.2))
        ex, ey = 170, 380
        glow_dot(c, ex, ey, 9, BLUE, a)
        text(c, "EARTH", ex + 26, ey + 8, 22, MIST, "mono", "l", a)
        line(c, ex + 10, ey + 20, ex + 60, ey + 110, MIST, 0.5 * a, 2, dash=[6, 8])
        text(c, "every phone, every second", ex + 20, ey + 150, 30, CREAM, "body", "l", a)
    if on(t, B, "howit"):
        c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, clamp((since(t, B, "howit") - 1.0) / 2.0) * 0.85))


# ============================== TITLE ==============================
def S_title(c, t, B, D):
    bg(c); STARS.draw(c, t, (6, 0), 0.9)
    p = clamp(t / 1.1)
    logo(c, W / 2, 400, 300 * back(p), a=p, spin=-90 * (1 - eo(p)) + t * 6)
    text_rise(c, "How Does GPS Know", W / 2, 690, 92, clamp((t - 0.5) / 0.7))
    text_rise(c, "Where You Are?", W / 2, 800, 92, clamp((t - 0.7) / 0.7), AMBER)
    text(c, "C O G S   &   C O S M O S", W / 2, 880, 24, MIST, "mono", "c", clamp((t - 1.2) / 0.8))
    vignette(c, 0.5)


# ============================== HOOK ==============================
def S_hook(c, t, B, D):
    bg(c); STARS.draw(c, t, (4, 0), 0.9)
    aB = xfade(t, B, "metres", 0.8)
    aC = xfade(t, B, "promise", 0.8)
    aA = 1 - aB
    if aA > 0.01:
        earth(c, 960, 1560, 960, rot=t * 0.02, a=aA)
        cx, cy, R = 960, 1560, 1360
        sats = []
        for k, ang in enumerate([-38, -20, 0, 18, 36]):
            th = math.radians(ang - 90 + t * 0.6)
            x, y = cx + R * math.cos(th), cy + R * math.sin(th)
            sats.append((x, y))
            satellite(c, x, y, 0.55, ang * 0.5, aA)
            ph = (t * 0.7 + k * 0.37) % 1
            ring(c, x, y, 20 + ph * 90, TEAL, aA * (1 - ph) * 0.7, 3)
            secs = (t + k * 0.13) % 60
            text(c, f"12:00:{secs:06.3f}", x, y - 54, 20, MIST, "mono", "c", aA * P(t, B, "sats", 0.8, 0.6))
        pd = P(t, B, "sats", 0.8, 2.0) * aA
        line(c, 1010, 600, 1010, 245, CREAM, 0.6 * pd, 2, dash=[10, 10])
        line(c, 995, 600, 1025, 600, CREAM, 0.6 * pd, 2); line(c, 995, 245, 1025, 245, CREAM, 0.6 * pd, 2)
        text(c, "≈ 20,000 km", 1050, 440, 40, CREAM, "head", "l", pd)
        if on(t, B, "listen"):
            al = P(t, B, "listen", 0.6) * aA
            px, py = 960, 600
            for (x, y) in sats:
                line(c, x, y + 30, px, py - 18, TEAL, 0.5 * al, 2, dash=[10, 12], phase=-since(t, B, "listen") * 60)
            rrect(c, px - 14, py - 26, 28, 50, 6, CREAM, al)
            arrow(c, px + 90, py - 30, px + 90, py - 120, RED, al * 0.9, 4)
            line(c, px + 72, py - 92, px + 108, py - 56, RED, al, 5); line(c, px + 108, py - 92, px + 72, py - 56, RED, al, 5)
            text(c, "no reply — it only listens", px + 130, py - 66, 34, CREAM, "body", "l", al)
    if aB > 0.01 and aC < 0.99:
        a = aB * (1 - aC)
        drift = eio((since(t, B, "drift") - 1.0) / 6.0) if on(t, B, "drift") else 0
        acc = lerp(150, 46, P(t, B, "metres", 2.0, 0.4))
        dotx = 0.5 + drift * 0.42
        phone(c, 960, 560, 1.0, t, dot=(dotx, 0.56), acc=acc, a=a, off=(-drift * 260, 0))
        text(c, "± a few metres", 470, 540, 54, CREAM, "head", "c", a * P(t, B, "metres", 0.7, 0.6) * (1 - P(t, B, "drift", 0.6)))
        if on(t, B, "drift"):
            ad = P(t, B, "drift", 0.7) * a
            text(c, "Without Einstein:", 1460, 470, 40, MIST, "body", "c", ad)
            text(c, "kilometres", 1460, 560, 72, AMBER, "head", "c", ad)
            text(c, "of drift, every day", 1460, 620, 40, CREAM, "body", "c", ad)
    if aC > 0.01:
        a = aC
        y = 470
        satellite(c, 520, y, 0.9, 0, a)
        text(c, "12:00:00.000", 520, y + 110, 30, MIST, "mono", "c", a)
        arrow(c, 660, y, 800, y, CREAM, a * P(t, B, "promise", 0.6, 0.6), 5)
        phone(c, 960, y, 0.32, t, dot=(0.5, 0.5), acc=20, a=a * P(t, B, "promise", 0.6, 0.9), draw_dot=False)
        arrow(c, 1120, y, 1260, y, CREAM, a * P(t, B, "promise", 0.6, 1.4), 5)
        if P(t, B, "promise", 0.6, 1.8) > 0: blue_dot(c, 1400, y, t, 50, a * P(t, B, "promise", 0.6, 1.8))
        text_rise(c, "clock readings from space → your blue dot", W / 2, 760, 48, (since(t, B, "promise") - 2.2) / 0.8, a=a)
        text_rise(c, "and why it only works because Einstein was right", W / 2, 840, 38, (since(t, B, "promise") - 4.5) / 0.8, AMBER, "body", a=a)
    vignette(c, 0.45)


# ============================== BEAT 1 ==============================
RAIN = [(random.Random(i).random() * W, random.Random(i * 7).random() * H, random.Random(i * 3).uniform(0.6, 1.4)) for i in range(140)]

def bolt_path(x, y0, y1, seed=4):
    rng = random.Random(seed); p = skia.Path(); p.moveTo(x, y0); xx = x
    n = 9
    for k in range(1, n + 1):
        yy = y0 + (y1 - y0) * k / n; xx = x + rng.uniform(-60, 60) if k < n else x
        p.lineTo(xx, yy)
    return p

def house(c, x, y, s=1.0, a=1.0):
    p = skia.Path(); p.moveTo(x - 90 * s, y); p.lineTo(x - 90 * s, y - 110 * s); p.lineTo(x, y - 190 * s); p.lineTo(x + 90 * s, y - 110 * s); p.lineTo(x + 90 * s, y); p.close()
    c.drawPath(p, paint(NAVY3, a)); c.drawPath(p, paint(MIST, 0.6 * a, stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(x - 25 * s, y - 70 * s, 50 * s, 40 * s), paint(AMBER, 0.85 * a))

def S_b1(c, t, B, D):
    bg(c, "#070A1A")
    a_storm = 1 - xfade(t, B, "same", 0.7)
    a_same = xfade(t, B, "same", 0.7) * (1 - xfade(t, B, "orbits", 0.7))
    a_orb = xfade(t, B, "orbits", 0.7)
    gx, gy, hx = 520, 860, 1480
    if a_storm > 0.01:
        a = a_storm
        for x, y, sp in RAIN:
            yy = (y + t * 900 * sp) % (H + 100) - 50; xx = (x + t * 120 * sp) % W
            line(c, xx, yy, xx + 10, yy + 40, MIST, 0.12 * a, 2)
        line(c, 0, gy, W, gy, MIST, 0.4 * a, 3)
        house(c, hx, gy, 1.0, a)
        if on(t, B, "flash"):
            s = since(t, B, "flash")
            for fl in (0.0, 0.22):
                k = clamp(1 - (s - fl) / 0.5) if s >= fl else 0
                if k > 0: c.drawRect(skia.Rect.MakeWH(W, H), paint(CREAM, 0.35 * k * a))
            bp = bolt_path(gx, 80, gy)
            ba = clamp(1 - (s - 0.3) / 2.5) * 0.9 + 0.1
            c.drawPath(bp, paint(CREAM, 0.6 * ba * a, stroke=16, blur=14)); c.drawPath(bp, paint("#FFFFFF", ba * a, stroke=6))
            text(c, "light: almost instant", gx + 60, 210, 34, CREAM, "body", "l", a * P(t, B, "sound", 0.6))
            if on(t, B, "sound"):
                ss = since(t, B, "sound")
                for k in range(3):
                    r = ((ss * 160) + k * 120) % 960
                    pth = skia.Path(); pth.addArc(skia.Rect.MakeLTRB(gx - r, gy - r, gx + r, gy + r), -60, 60)
                    c.drawPath(pth, paint(TEAL, a * 0.8 * (1 - r / 960), stroke=5))
                text(c, "sound: 340 m/s", 1010, 560, 44, TEAL, "head", "c", a * P(t, B, "sound", 0.6, 0.8))
        if on(t, B, "km"):
            s = since(t, B, "km"); a2 = P(t, B, "km", 0.4) * a
            n = min(3, int(s / 0.9) + 1)
            text(c, "1   2   3"[:max(1, (n - 1) * 4 + 1)], W / 2, 340, 120, CREAM, "mono", "c", a2)
            pd = P(t, B, "km", 0.6, 2.6) * a
            line(c, gx, gy + 60, hx, gy + 60, AMBER, pd, 4); line(c, gx, gy + 40, gx, gy + 80, AMBER, pd, 4); line(c, hx, gy + 40, hx, gy + 80, AMBER, pd, 4)
            text(c, "≈ 1 km", (gx + hx) / 2, gy + 140, 64, AMBER, "head", "c", pd)
    if a_same > 0.01:
        a = a_same
        text_rise(c, "TIME  →  DISTANCE", W / 2, 520, 120, (since(t, B, "same") - 0.2) / 0.7, a=a)
        pr = P(t, B, "same", 0.8, 2.4) * a
        text(c, "GPS: radio waves instead of sound", W / 2, 640, 44, AMBER, "body", "c", pr)
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            pth = skia.Path(); r = 40 + ph * 160
            pth.addArc(skia.Rect.MakeLTRB(W / 2 - r, 820 - r, W / 2 + r, 820 + r), -130, 80)
            c.drawPath(pth, paint(TEAL, pr * (1 - ph), stroke=5))
    if a_orb > 0.01:
        a = a_orb
        chapter_tag(c, 1, "time becomes distance", a)
        ex, ey, er = 960, 560, 170
        layout2 = xfade(t, B, "message", 0.7)
        layout3 = xfade(t, B, "travel", 0.7)
        layout4 = xfade(t, B, "compute", 0.6)
        a1 = a * (1 - layout2)
        if a1 > 0.01:
            orbs = [(420, 130, ang) for ang in (0, 30, 60, 90, 120, 150)]
            dots = []
            for oi, (rx, ry, ang) in enumerate(orbs):
                orbit_ellipse(c, ex, ey, rx, ry, ang, CREAM, 0.2 * a1, 2)
                for k in range(4):
                    th = t * 0.35 + k * math.pi / 2 + oi * 0.5
                    dots.append(orbit_point(ex, ey, rx, ry, ang, th))
            for x, y, depth in dots:
                if depth < 0: glow_dot(c, x, y, 5, AMBER, 0.5 * a1)
            earth(c, ex, ey, er, t * 0.15, a1)
            for x, y, depth in dots:
                if depth >= 0: glow_dot(c, x, y, 7, AMBER, a1)
            for i, (lab, x, y, al) in enumerate([("30+ satellites", 300, 380, "l"), ("6 orbits", 300, 470, "l"), ("20,200 km up", W - 300, 380, "r"), ("2 laps a day", W - 300, 470, "r")]):
                text(c, lab, x, y, 46, CREAM if i % 2 == 0 else AMBER, "head", al, a1 * P(t, B, "orbits", 0.6, 1.0 + i * 1.6))
        if layout2 > 0.01 and layout3 < 0.99:
            a2 = a * layout2 * (1 - layout3)
            satellite(c, 520, 520, 1.7, -8 + 3 * math.sin(t), a2)
            ph = (t * 0.8) % 1; ring(c, 520, 520, 60 + ph * 220, TEAL, a2 * (1 - ph), 4)
            rrect(c, 860, 300, 880, 400, 22, NAVY2, 0.92 * a2); rrect(c, 860, 300, 880, 400, 22, TEAL, 0.6 * a2, stroke=2)
            s = since(t, B, "message")
            lines = [("I AM:", "SATELLITE 12"), ("I AM HERE:", "x · y · z"), ("THE TIME IS:", "12:00:00.000000000")]
            for k, (lab, val) in enumerate(lines):
                pk = clamp((s - 1.5 - k * 2.4) / 1.2)
                text(c, lab, 900, 400 + k * 110, 26, MIST, "mono", "l", a2 * clamp(pk * 3))
                typewriter(c, val, 1140, 400 + k * 110, 38, pk, AMBER if k == 2 else CREAM, cursor=False, a=a2)
            if on(t, B, "light"):
                al = P(t, B, "light", 0.6) * a2
                sx = ((since(t, B, "light") * 1400) % 2600) - 300
                c.drawLine(sx - 400, 860, sx, 860, paint(CREAM, 0.5 * al, stroke=8, blur=8)); c.drawLine(sx - 300, 860, sx, 860, paint("#FFFFFF", al, stroke=3))
                text(c, "speed of light ≈ 300,000 km/s", W / 2, 800, 52, CREAM, "head", "c", al)
        if layout3 > 0.01 and layout4 < 0.99:
            a3 = a * layout3 * (1 - layout4)
            sx, sy, px, py = 960, 210, 960, 860
            satellite(c, sx, sy, 0.9, 0, a3)
            phone(c, px, py, 0.32, t, dot=(0.5, 0.5), acc=16, a=a3)
            s = since(t, B, "travel")
            k = (s % 2.4) / 2.0
            line(c, sx, sy + 40, px, py - 130, TEAL, 0.25 * a3, 2, dash=[8, 10])
            if k <= 1:
                yy = lerp(sy + 40, py - 130, eio(k)); glow_dot(c, sx, yy, 10, TEAL, a3)
            frac = clamp(k)
            text(c, "SENT", 520, 250, 26, MIST, "mono", "c", a3); text(c, "12:00:00.0000", 520, 300, 40, CREAM, "mono", "c", a3)
            text(c, "ARRIVED", 1400, 760, 26, MIST, "mono", "c", a3); text(c, f"12:00:00.{int(674 * frac):04d}", 1400, 810, 40, AMBER, "mono", "c", a3)
            text(c, f"{0.0674 * frac:.3f} s", 1400, 520, 90, AMBER, "head", "c", a3)
        if layout4 > 0.01:
            a4 = a * layout4 * (1 - xfade(t, B, "idea", 0.6))
            text_rise(c, "distance = travel time × speed of light", W / 2, 470, 64, (since(t, B, "compute") - 0.3) / 0.7, a=a4)
            text(c, "0.0674 s × 299,792 km/s ≈ 20,200 km", W / 2, 590, 50, AMBER, "mono", "c", a4 * P(t, B, "compute", 0.7, 2.5))
            ai = xfade(t, B, "idea", 0.6) * a
            text_rise(c, "GPS doesn't measure where you are.", W / 2, 470, 66, (since(t, B, "idea") - 0.2) / 0.7, a=ai)
            text_rise(c, "It measures how long a signal took.", W / 2, 580, 66, (since(t, B, "idea") - 2.2) / 0.7, AMBER, a=ai)
    vignette(c, 0.45)


# ============================== BEAT 2 ==============================
def train_icon(c, x, y, s=1.0, a=1.0):
    rrect(c, x - 50 * s, y - 60 * s, 100 * s, 110 * s, 18 * s, AMBER, a)
    rrect(c, x - 36 * s, y - 46 * s, 72 * s, 40 * s, 8 * s, NAVY, a)
    c.drawCircle(x - 26 * s, y + 22 * s, 9 * s, paint(NAVY, a)); c.drawCircle(x + 26 * s, y + 22 * s, 9 * s, paint(NAVY, a))
    line(c, x - 40 * s, y + 70 * s, x - 56 * s, y + 92 * s, AMBER, a, 6 * s); line(c, x + 40 * s, y + 70 * s, x + 56 * s, y + 92 * s, AMBER, a, 6 * s)

def circle_intersections(x0, y0, r0, x1, y1, r1):
    d = math.hypot(x1 - x0, y1 - y0)
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d); h = math.sqrt(max(r0 * r0 - a * a, 0))
    xm = x0 + a * (x1 - x0) / d; ym = y0 + a * (y1 - y0) / d
    return (xm + h * (y1 - y0) / d, ym - h * (x1 - x0) / d), (xm - h * (y1 - y0) / d, ym + h * (x1 - x0) / d)

def atom(c, x, y, s=1.0, t=0.0, a=1.0):
    for k in range(3):
        c.save(); c.translate(x, y); c.rotate(k * 60 + t * 20)
        c.drawOval(skia.Rect.MakeLTRB(-90 * s, -32 * s, 90 * s, 32 * s), paint(TEAL, 0.8 * a, stroke=4 * s))
        th = t * 2.2 + k * 2.1
        c.drawCircle(90 * s * math.cos(th), 32 * s * math.sin(th), 8 * s, paint(CREAM, a))
        c.restore()
    glow_dot(c, x, y, 14 * s, AMBER, a)

def S_b2(c, t, B, D):
    bg(c)
    chapter_tag(c, 2, "why four satellites", 1.0)
    a_map = 1 - xfade(t, B, "sphere", 0.7)
    a_sp = xfade(t, B, "sphere", 0.7) * (1 - xfade(t, B, "four", 0.6))
    a_four = xfade(t, B, "four", 0.6) * (1 - xfade(t, B, "quartz", 0.6))
    a_q = xfade(t, B, "quartz", 0.6) * (1 - xfade(t, B, "unknowns", 0.6))
    a_u = xfade(t, B, "unknowns", 0.6)
    if a_map > 0.01:
        a = a_map
        c.save(); c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, 1)); map_screen(c, 0, 0, W, H, (t * 6, 0), 0.55 * a); c.restore()
        c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, 0.35 * a))
        train_icon(c, 960, 540, 1.0, a * P(t, B, "one", 0.6))
        if on(t, B, "station"):
            r = 330 * P(t, B, "station", 1.4, 0.6)
            ring(c, 960, 540, r, TEAL, a, 5)
            c.drawCircle(960, 540, r, paint(TEAL, 0.07 * a))
            line(c, 960, 540, 960 + r, 540, CREAM, 0.7 * a, 3, dash=[10, 8])
            text(c, "5 km", 960 + r / 2, 525, 38, CREAM, "head", "c", a * P(t, B, "station", 0.5, 1.6))
            for k in range(7):
                th = k * 2 * math.pi / 7 + 0.4
                text(c, "?", 960 + 330 * math.cos(th), 540 + 330 * math.sin(th) + 18, 54, AMBER, "head", "c", a * P(t, B, "station", 0.4, 2.2 + k * 0.25))
    if a_sp > 0.01:
        a = a_sp
        STARS2.draw(c, t, (3, 0), 0.7 * a)
        ecx, ecy, er = 960, 1340, 610
        earth(c, ecx, ecy, er, t * 0.02, a)
        Pt = (1010, ecy - math.sqrt(er * er - 50 * 50))
        S = [(420, 466), (1600, 466), (300, 150)]
        rad = [math.hypot(sx - Pt[0], sy - Pt[1]) for sx, sy in S]
        for k, beat in enumerate(["sphere", "two", "three"]):
            if not on(t, B, beat): continue
            pk = P(t, B, beat, 1.4, 0.3)
            r = rad[k] * pk
            sx, sy = S[k]
            c.drawCircle(sx, sy, r, paint(TEAL, 0.05 * a)); ring(c, sx, sy, r, TEAL, 0.7 * a, 3)
            satellite(c, sx, sy, 0.55, 0, a)
        if on(t, B, "sphere"):
            pl = a * P(t, B, "sphere", 0.5, 1.6) * (1 - P(t, B, "two", 0.5))
            line(c, S[0][0], S[0][1], Pt[0], Pt[1], CREAM, 0.7 * pl, 3, dash=[10, 8])
            text(c, "21,000 km", 640, 560, 40, CREAM, "head", "c", pl)
        if on(t, B, "two"):
            i1, i2 = circle_intersections(S[0][0], S[0][1], rad[0], S[1][0], S[1][1], rad[1])
            pk = P(t, B, "two", 0.8, 1.6) * a
            mx, my = (i1[0] + i2[0]) / 2, (i1[1] + i2[1]) / 2
            L = math.hypot(i1[0] - i2[0], i1[1] - i2[1]); ang = math.degrees(math.atan2(i2[1] - i1[1], i2[0] - i1[0]))
            c.save(); c.translate(mx, my); c.rotate(ang)
            c.drawOval(skia.Rect.MakeLTRB(-L / 2, -L * 0.13, L / 2, L * 0.13), paint(AMBER, 0.9 * pk, stroke=5)); c.restore()
            if on(t, B, "three"):
                p3 = P(t, B, "three", 0.6, 1.6)
                far = i1 if i1[1] < i2[1] else i2
                near = i2 if far is i1 else i1
                glow_dot(c, far[0], far[1], 12, AMBER, a * p3 * (1 - P(t, B, "three", 0.6, 4.0)))
                glow_dot(c, near[0], near[1], 12, AMBER, a * p3)
                xa = a * P(t, B, "three", 0.4, 4.0)
                line(c, far[0] - 26, far[1] - 26, far[0] + 26, far[1] + 26, RED, xa, 6); line(c, far[0] + 26, far[1] - 26, far[0] - 26, far[1] + 26, RED, xa, 6)
                text(c, "out in space", far[0] + 40, far[1] - 30, 32, RED, "body", "l", xa)
            if on(t, B, "trilat"):
                at = P(t, B, "trilat", 0.6)
                near = i2 if (i1[1] < i2[1]) else i1
                blue_dot(c, near[0], near[1], t, 40, a * at)
                text(c, "TRILATERATION", W / 2, 560, 80, CREAM, "head", "c", a * at)
    if a_four > 0.01:
        text_rise(c, "So why", W / 2, 420, 70, (since(t, B, "four") - 0.1) / 0.6, MIST, "body", a=a_four)
        text(c, "4?", W / 2, 640, 240, AMBER, "head", "c", a_four * P(t, B, "four", 0.5, 0.5))
    if a_q > 0.01:
        a = a_q
        satellite(c, 560, 380, 1.2, 0, a); atom(c, 560, 600, 0.9, t, a)
        text(c, "satellite: atomic clocks", 560, 780, 44, CREAM, "head", "c", a)
        line(c, W / 2, 260, W / 2, 820, MIST, 0.3 * a, 2)
        clock_face(c, 1360, 480, 140, t * 0.4 + 0.05 * math.sin(t * 3.1), CREAM, a * P(t, B, "quartz", 0.6, 2.0))
        text(c, "your phone: cheap quartz clock", 1360, 780, 44, AMBER, "head", "c", a * P(t, B, "quartz", 0.6, 2.0))
    if a_u > 0.01:
        a = a_u
        labels = ["EAST–WEST", "NORTH–SOUTH", "UP–DOWN", "CLOCK ERROR"]
        x0 = 150; w = 380; gap = 30
        a_b = xfade(t, B, "borrow", 0.6)
        for k, lab in enumerate(labels):
            pk = P(t, B, "unknowns", 0.5, 3.2 + k * 1.1) * a * (1 - a_b)
            x = x0 + k * (w + gap)
            rrect(c, x, 400, w, 230, 22, NAVY2, pk); rrect(c, x, 400, w, 230, 22, AMBER if k == 3 else TEAL, pk, stroke=3)
            text(c, lab, x + w / 2, 535, 40, AMBER if k == 3 else CREAM, "head", "c", pk)
            text(c, f"unknown {k + 1}", x + w / 2, 590, 24, MIST, "body", "c", pk)
        text_rise(c, "one more unknown: your phone's clock error", W / 2, 300, 46, (since(t, B, "unknowns") - 0.2) / 0.7, a=a * (1 - a_b))
        if a_b > 0.01:
            pos = [(380, 220), (760, 140), (1160, 140), (1540, 220)]
            px, py = 960, 760
            for k, (x, y) in enumerate(pos):
                pk = P(t, B, "borrow", 0.6, k * 0.3) * a_b
                satellite(c, x, y, 0.55, 0, pk)
                line(c, x, y + 30, px, py - 120, TEAL, 0.6 * pk, 3, dash=[10, 10], phase=-t * 40)
            phone(c, px, py, 0.34, t, dot=(0.5, 0.5), acc=14, a=a_b)
            text(c, "4 unknowns  →  4 measurements", W / 2, 470, 56, AMBER, "head", "c", a_b * P(t, B, "borrow", 0.6, 1.2))
            text(c, "a precise clock, borrowed from space", W / 2, 1000, 36, CREAM, "body", "c", a_b * P(t, B, "borrow", 0.6, 4.0))
    vignette(c, 0.45)


# ============================== BEAT 3 ==============================
def ruler(c, x, y, w, h, a=1.0):
    rrect(c, x, y, w, h, 10, AMBER, a)
    for k in range(31):
        L = h * (0.55 if k % 10 == 0 else 0.35 if k % 5 == 0 else 0.2)
        xx = x + 20 + k * (w - 40) / 30
        line(c, xx, y, xx, y + L, NAVY, a, 3)
    text(c, "30 cm", x + w - 30, y + h - 22, 30, NAVY, "head", "r", a)

def dish(c, x, y, s=1.0, a=1.0):
    pth = skia.Path(); pth.addArc(skia.Rect.MakeLTRB(x - 70 * s, y - 70 * s, x + 70 * s, y + 70 * s), 200, 140)
    c.drawPath(pth, paint(CREAM, a, stroke=10 * s))
    line(c, x, y + 20 * s, x, y + 80 * s, CREAM, a, 8 * s); line(c, x - 40 * s, y + 80 * s, x + 40 * s, y + 80 * s, CREAM, a, 8 * s)
    line(c, x, y - 10 * s, x + 30 * s, y - 60 * s, MIST, a, 4 * s)

def tick(c, x, y, s=1.0, color=TEAL, a=1.0):
    pth = skia.Path(); pth.moveTo(x - 14 * s, y); pth.lineTo(x - 4 * s, y + 11 * s); pth.lineTo(x + 16 * s, y - 13 * s)
    c.drawPath(pth, paint(color, a, stroke=6 * s))

def S_b3(c, t, B, D):
    bg(c)
    chapter_tag(c, 3, "clocks that can't be wrong", 1.0)
    phases = ["fast", "ns", "us", "atomic", "ground", "five", "city", "problem"]
    def A(beat, nxt):
        return xfade(t, B, beat, 0.6) * (1 - (xfade(t, B, nxt, 0.6) if nxt else 0))
    a_fast = A("fast", "ns"); a_ns = A("ns", "us"); a_us = A("us", "atomic"); a_at = A("atomic", "ground")
    a_gr = A("ground", "five"); a_five = A("five", "city"); a_city = A("city", "problem"); a_pr = A("problem", None)
    if a_fast > 0.01:
        sx = ((since(t, B, "fast") * 1600) % 2800) - 400
        c.drawLine(sx - 500, 600, sx, 600, paint(CREAM, 0.5 * a_fast, stroke=10, blur=10)); c.drawLine(sx - 380, 600, sx, 600, paint("#FFFFFF", a_fast, stroke=4))
        text_rise(c, "Light is ridiculously fast.", W / 2, 440, 76, (since(t, B, "fast") - 0.2) / 0.6, a=a_fast)
    if a_ns > 0.01:
        a = a_ns
        ruler(c, 510, 520, 900, 120, a * P(t, B, "ns", 0.6, 0.3))
        text_rise(c, "1 nanosecond", W / 2, 400, 80, (since(t, B, "ns") - 0.2) / 0.6, a=a)
        text(c, "light travels ≈ 30 cm — about a ruler", W / 2, 760, 44, AMBER, "body", "c", a * P(t, B, "ns", 0.6, 3.0))
    if a_us > 0.01:
        a = a_us
        z = P(t, B, "us", 2.0)
        c.save(); c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY)); map_screen(c, 0, 0, W, H, (0, 0), 0.6 * a * z); c.restore()
        c.drawRect(skia.Rect.MakeWH(W, H), paint(NAVY, 0.3 * a))
        ruler(c, lerp(510, 950, z), lerp(520, 595, z), lerp(900, 18, z), lerp(120, 6, z), a * (1 - z * 0.6))
        x1, x2, y = 560, 1360, 640
        pd = P(t, B, "us", 0.6, 2.2) * a
        for x, lab in [(x1, "front door"), (x2, "next street")]:
            c.drawCircle(x, y - 40, 22, paint(RED if x == x2 else BLUE, pd)); c.drawCircle(x, y - 40, 8, paint(CREAM, pd))
            text(c, lab, x, y + 40, 34, CREAM, "body", "c", pd)
        line(c, x1, y - 40, x2, y - 40, AMBER, pd, 5, dash=[16, 10])
        text(c, "1 microsecond off  ≈  300 m", W / 2, 300, 66, AMBER, "head", "c", a * P(t, B, "us", 0.6, 1.0))
    if a_at > 0.01:
        a = a_at
        satellite(c, 520, 520, 1.8, -6, a)
        atom(c, 1240, 470, 1.4, t, a * P(t, B, "atomic", 0.6, 0.6))
        text(c, "several atomic clocks", 1240, 720, 50, CREAM, "head", "c", a * P(t, B, "atomic", 0.6, 1.0))
        text(c, "accurate to a few billionths of a second", 1240, 790, 34, AMBER, "body", "c", a * P(t, B, "atomic", 0.6, 4.0))
    if a_gr > 0.01:
        a = a_gr
        earth(c, 960, 1700, 900, t * 0.02, a)
        sx, sy = 1300 + 40 * math.sin(t * 0.3), 300
        satellite(c, sx, sy, 0.8, 0, a)
        dish(c, 640, 760, 1.0, a)
        s = since(t, B, "ground")
        for k in range(3):
            ph = (s * 0.7 + k / 3) % 1
            glow_dot(c, lerp(670, sx, ph), lerp(700, sy + 30, ph), 7, TEAL, a * (1 - abs(ph - 0.5) * 1.4))
        for k, lab in enumerate(["check the clocks", "track every orbit", "upload corrections"]):
            pk = P(t, B, "ground", 0.5, 1.0 + k * 1.6) * a
            tick(c, 1180, 520 + k * 80, 1.2, TEAL, pk); text(c, lab, 1220, 532 + k * 80, 40, CREAM, "body", "l", pk)
    if a_five > 0.01:
        a = a_five
        phone(c, 960, 540, 1.0, t, dot=(0.5, 0.52), acc=lerp(140, 52, P(t, B, "five", 1.6, 0.3)), a=a)
        text(c, "≈ 5 m", 520, 520, 90, AMBER, "head", "c", a * P(t, B, "five", 0.6, 1.0))
        text(c, "under open sky", 520, 600, 40, CREAM, "body", "c", a * P(t, B, "five", 0.6, 1.4))
    if a_city > 0.01:
        a = a_city
        rng = random.Random(9)
        for k in range(9):
            x = 160 + k * 190; h = rng.uniform(260, 600); w = 150
            c.drawRect(skia.Rect.MakeXYWH(x, 900 - h, w, h), paint(NAVY3, a))
            for wy in range(int(900 - h + 30), 880, 46):
                for wx in range(int(x + 18), int(x + w - 20), 38):
                    if rng.random() < 0.55: c.drawRect(skia.Rect.MakeXYWH(wx, wy, 18, 24), paint(AMBER, 0.35 * a))
        line(c, 0, 900, W, 900, MIST, 0.5 * a, 3)
        satellite(c, 300, 150, 0.6, 0, a)
        s = since(t, B, "city"); pk = clamp((s - 0.8) / 2.0)
        bx, by = 1370, 420; gx, gy = 1040, 880
        line(c, 330, 180, lerp(330, bx, pk), lerp(180, by, pk), TEAL, a, 4, dash=[12, 8])
        if pk >= 1:
            p2 = clamp((s - 2.8) / 1.2); line(c, bx, by, lerp(bx, gx, p2), lerp(by, gy, p2), TEAL, a, 4, dash=[12, 8])
            text(c, "bounced = late", bx + 30, by - 20, 36, TEAL, "body", "l", a * p2)
        jump = P(t, B, "city", 0.25, 5.0)
        dx = lerp(900, 1180, jump)
        c.drawCircle(dx, 960, 16, paint("#FFFFFF", a)); c.drawCircle(dx, 960, 11, paint(BLUE, a))
        text(c, "your blue dot jumps the road", W / 2, 1030, 38, CREAM, "body", "c", a * P(t, B, "city", 0.5, 5.0))
    if a_pr > 0.01:
        a = a_pr
        wob = 0.08 * math.sin(t * 2.3)
        c.save(); c.translate(W / 2, 470); c.scale(1 + wob, 1 - wob); clock_face(c, 0, 0, 170, t * 1.7, CREAM, a, 1.0); c.restore()
        text_rise(c, "a problem with time itself", W / 2, 800, 70, (since(t, B, "problem") - 4.0) / 1.0, AMBER, a=a)
    vignette(c, 0.45)


# ============================== TWIST ==============================
def well(c, cx, cy, a=1.0, depth=320):
    for k in range(-10, 11):
        x0 = cx + k * 90
        pth = skia.Path()
        for j in range(0, 41):
            y = 300 + j * 18
            dx = x0 - cx; dy = y - cy
            d = math.hypot(dx * 0.7, dy)
            sink = depth * math.exp(-(d / 320) ** 2)
            X = x0 - dx * 0.25 * math.exp(-(d / 320) ** 2); Y = y + sink * 0.4
            (pth.moveTo if j == 0 else pth.lineTo)(X, Y)
        c.drawPath(pth, paint(TEAL, 0.18 * a, stroke=2))
    for j in range(0, 14):
        y0 = 300 + j * 52
        pth = skia.Path()
        for k in range(0, 61):
            x = cx - 900 + k * 30
            dx = x - cx; dy = y0 - cy
            d = math.hypot(dx * 0.7, dy)
            Y = y0 + depth * 0.4 * math.exp(-(d / 320) ** 2)
            (pth.moveTo if k == 0 else pth.lineTo)(x, Y)
        c.drawPath(pth, paint(TEAL, 0.18 * a, stroke=2))

def S_tw(c, t, B, D):
    bg(c); STARS.draw(c, t, (3, 0), 0.5)
    chapter_tag(c, 4, "einstein's problem", 1.0)
    def A(beat, nxt):
        return xfade(t, B, beat, 0.6) * (1 - (xfade(t, B, nxt, 0.6) if nxt else 0))
    a_y = A("years", "caught"); a_c = A("caught", "sr"); a_sr = A("sr", "gr"); a_gr = A("gr", "net")
    a_net = A("net", "eleven"); a_el = A("eleven", "tune"); a_tu = A("tune", "1977"); a_77 = A("1977", None)
    if a_y > 0.01:
        text_rise(c, "1905", 620, 560, 220, (since(t, B, "years") - 0.2) / 0.7, CREAM, a=a_y)
        text_rise(c, "1915", 1300, 560, 220, (since(t, B, "years") - 1.4) / 0.7, AMBER, a=a_y)
        text(c, "time doesn't tick at the same rate for everyone", W / 2, 720, 44, MIST, "body", "c", a_y * P(t, B, "years", 0.6, 3.5))
    if a_c > 0.01:
        a = a_c
        satellite(c, 960, 520, 1.3, 0, a)
        pk = P(t, B, "caught", 0.7, 0.6) * a
        arrow(c, 760, 520, 360 - 20 * math.sin(t * 3), 520, TEAL, pk, 8, 30)
        arrow(c, 1160, 520, 1560 + 20 * math.sin(t * 3), 520, AMBER, pk, 8, 30)
        text(c, "speed", 520, 470, 50, TEAL, "head", "c", pk); text(c, "gravity", 1400, 470, 50, AMBER, "head", "c", pk)
    if a_sr > 0.01:
        a = a_sr
        text(c, "SPECIAL RELATIVITY", 120, 220, 64, CREAM, "head", "l", a)
        text(c, "moving clocks run slow", 120, 290, 40, TEAL, "body", "l", a)
        sx = 760 + 30 * math.sin(t * 0.8)
        for k in range(6):
            yy = 560 + (k - 2.5) * 26
            ph = (t * 3 + k * 0.37) % 1
            line(c, sx - 140 - ph * 260, yy, sx - 120 - ph * 260 + 140, yy, TEAL, a * 0.6 * (1 - ph), 4)
        satellite(c, sx, 560, 1.2, 0, a)
        text(c, "≈ 3.9 km/s  ·  14,000 km/h", 760, 760, 40, CREAM, "body", "c", a * P(t, B, "speed", 0.6, 0.6))
        pk = P(t, B, "speed", 0.6, 3.5) * a
        clock_face(c, 1460, 520, 130, t * 0.3, CREAM, pk)
        text(c, "− 7 µs / day", 1460, 740, 64, TEAL, "head", "c", pk)
    if a_gr > 0.01:
        a = a_gr
        ecx, ecy = 960, 820
        well(c, ecx, ecy - 200, a)
        earth(c, ecx, ecy, 120, t * 0.2, a)
        text(c, "GENERAL RELATIVITY", 120, 220, 64, CREAM, "head", "l", a)
        text(c, "gravity slows time", 120, 290, 40, AMBER, "body", "l", a)
        ph = P(t, B, "high", 0.7)
        satellite(c, 1470, 360, 0.8, 0, a * ph)
        clock_face(c, 1470, 560, 90, t * 0.6, CREAM, a * ph)
        text(c, "+ 45 µs / day", 1470, 720, 58, AMBER, "head", "c", a * ph)
        clock_face(c, 700, 720, 64, t * 0.4, MIST, a * ph * 0.8)
        line(c, 760, 750, 850, 790, MIST, 0.5 * a * ph, 2, dash=[6, 8])
        text(c, "you, deeper in the well", 700, 840, 32, MIST, "body", "c", a * ph)
    if a_net > 0.01:
        a = a_net
        text(c, "− 7  +  45  =", 860, 560, 110, CREAM, "head", "r", a * P(t, B, "net", 0.6, 0.2))
        text(c, "+38 µs", 900, 560, 150, AMBER, "head", "l", a * P(t, B, "net", 0.6, 2.4))
        text(c, "gained by every GPS satellite clock, every day", W / 2, 700, 40, MIST, "body", "c", a * P(t, B, "net", 0.6, 3.2))
    if a_el > 0.01:
        a = a_el
        text_rise(c, "38 µs  ×  speed of light  ≈  11.4 km", W / 2, 360, 70, (since(t, B, "eleven") - 2.6) / 0.7, a=a)
        pk = P(t, B, "eleven", 2.4, 4.2)
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(260, 480, 1400, 300), 18, 18), doAntiAlias=True)
        map_screen(c, 260, 480, 1400, 300, (t * 10, 0), 0.6 * a); c.restore()
        rrect(c, 260, 480, 1400, 300, 18, TEAL, 0.5 * a, stroke=2)
        line(c, 360, 630, lerp(360, 1560, pk), 630, RED, a, 8)
        c.drawCircle(360, 630, 14, paint(BLUE, a)); c.drawCircle(lerp(360, 1560, pk), 630, 14, paint(RED, a * clamp(pk * 5)))
        text(c, "of error — every single day", W / 2, 880, 50, AMBER, "head", "c", a * P(t, B, "eleven", 0.6, 6.0))
    if a_tu > 0.01:
        a = a_tu
        rrect(c, 360, 300, 1200, 420, 28, NAVY2, 0.95 * a); rrect(c, 360, 300, 1200, 420, 28, TEAL, 0.6 * a, stroke=2)
        text(c, "SATELLITE CLOCK FREQUENCY", W / 2, 380, 30, MIST, "mono", "c", a)
        s = since(t, B, "tune"); k = clamp((s - 6.0) / 5.0)
        old_a = a * (1 - clamp((s - 5.0) / 0.8))
        w0 = text(c, "10.23 MHz", W / 2, 560 - 120 * clamp((s - 5.0) / 0.8), 104, CREAM, "mono", "c", old_a)
        if s > 4.2:
            ls = clamp((s - 4.2) / 0.6)
            line(c, W / 2 - w0 / 2, 520 - 120 * clamp((s - 5.0) / 0.8), W / 2 - w0 / 2 + w0 * ls, 520 - 120 * clamp((s - 5.0) / 0.8), RED, old_a, 6)
        if k > 0:
            full = "10.22999999543 MHz"; wf = tw(full, 104, "mono")
            typewriter(c, full, W / 2 - wf / 2, 560, 104, k, AMBER, cursor=False, a=a)
        text(c, "tuned slightly slow, before launch", W / 2, 660, 38, CREAM, "body", "c", a * clamp((s - 3) / 0.8))
        if on(t, B, "orbit"):
            po = P(t, B, "orbit", 0.6)
            text(c, "in orbit, relativity speeds it up → 10.23 MHz, as seen from the ground", W / 2, 830, 34, TEAL, "body", "c", a * po)
            tick(c, 280, 820, 1.4, TEAL, a * po)
    if a_77 > 0.01:
        a = a_77
        s = since(t, B, "1977")
        text_rise(c, "1977", 420, 330, 150, (s - 0.2) / 0.7, CREAM, a=a)
        rise = clamp((s - 1.0) / 6.0)
        sy = lerp(760, 380, eio(rise))
        for k in range(14):
            ph = (t * 2 + k / 14) % 1
            c.drawCircle(420 + math.sin(k * 3.1) * 10, sy + 50 + ph * 260, 14 * (1 - ph), paint(AMBER, a * 0.6 * (1 - ph)))
        satellite(c, 420, sy, 0.8, 0, a)
        # switch
        on_ = on(t, B, "proved", 4.0)
        sw = P(t, B, "proved", 0.4, 4.0)
        rrect(c, 760, 230, 260, 90, 45, TEAL if on_ else "#3A4470", a)
        c.drawCircle(lerp(805, 975, sw), 275, 36, paint(CREAM, a))
        text(c, "relativity correction", 1050, 270, 34, CREAM, "body", "l", a)
        text(c, "ON" if on_ else "OFF for 20 days", 1050, 312, 30, TEAL if on_ else RED, "mono", "l", a)
        # graph
        gx0, gy0, gw, gh = 760, 420, 980, 480
        line(c, gx0, gy0 + gh, gx0 + gw, gy0 + gh, MIST, 0.7 * a, 3); line(c, gx0, gy0, gx0, gy0 + gh, MIST, 0.7 * a, 3)
        text(c, "days →", gx0 + gw, gy0 + gh + 44, 28, MIST, "body", "r", a)
        text(c, "clock drift", gx0 - 16, gy0 - 16, 28, MIST, "body", "l", a)
        pg = clamp((s - 2.0) / 5.0)
        line(c, gx0, gy0 + gh, lerp(gx0, gx0 + gw, pg), lerp(gy0 + gh, gy0 + 40, pg), AMBER, a, 4, dash=[16, 12])
        text(c, "Einstein's prediction", gx0 + gw - 10, gy0 + 20, 30, AMBER, "body", "r", a * clamp(pg * 3 - 2))
        if on(t, B, "proved"):
            pd = clamp(since(t, B, "proved") / 3.0)
            for k in range(1, 11):
                if k / 10 <= pd:
                    x = gx0 + gw * k / 10; y = gy0 + gh - (gh - 40) * k / 10 + (4 if k % 2 else -4)
                    glow_dot(c, x, y, 9, TEAL, a)
            text(c, "measured", gx0 + gw * 0.55, gy0 + gh * 0.62, 30, TEAL, "body", "l", a * pd)
    vignette(c, 0.45)


# ============================== ANSWER ==============================
def S_ans(c, t, B, D):
    bg(c); STARS.draw(c, t, (3, 0), 0.6)
    chapter_tag(c, 5, "so how does gps know?", 1.0)
    a1 = 1 - xfade(t, B, "recap", 0.6)
    a2 = xfade(t, B, "recap", 0.6) * (1 - xfade(t, B, "gnss", 0.6))
    a3 = xfade(t, B, "gnss", 0.6)
    if a1 > 0.01:
        phone(c, 960, 560, 0.9, t, dot=(0.5, 0.55), acc=46, a=a1)
        text(c, "GPS doesn't know.", 420, 540, 52, CREAM, "head", "c", a1 * P(t, B, "doesnt", 0.6, 1.8))
        text(c, "Your phone works it out.", 1500, 540, 52, AMBER, "head", "c", a1 * P(t, B, "doesnt", 0.6, 3.2))
    if a2 > 0.01:
        steps = [("1", "Listen to 4+", "satellites"), ("2", "Time", "→ distance"), ("3", "Solve its", "own clock"), ("4", "Trust clocks", "set for Einstein")]
        for k, (n, l1, l2) in enumerate(steps):
            pk = P(t, B, "recap", 0.5, 0.4 + k * 2.2) * a2
            x = 150 + k * 420
            rrect(c, x, 360, 380, 360, 26, NAVY2, pk); rrect(c, x, 360, 380, 360, 26, AMBER if k == 3 else TEAL, pk, stroke=3)
            c.drawCircle(x + 190, 450, 44, paint(AMBER, pk)); text(c, n, x + 190, 468, 50, NAVY, "head", "c", pk)
            text(c, l1, x + 190, 590, 42, CREAM, "head", "c", pk); text(c, l2, x + 190, 646, 38, MIST, "body", "c", pk)
    if a3 > 0.01:
        ex, ey = 960, 540
        systems = [("GPS", AMBER, 0, 470, 150), ("Galileo", TEAL, 36, 430, 140), ("GLONASS", BLUE, 72, 450, 120), ("BeiDou", CREAM, 108, 410, 150), ("NavIC", "#FF8FB1", 144, 330, 110)]
        for k, (nm, colr, ang, rx, ry) in enumerate(systems):
            pk = P(t, B, "gnss", 0.6, 1.0 + k * 1.3) * a3
            orbit_ellipse(c, ex, ey, rx, ry, ang, colr, 0.55 * pk, 3)
            x, y, _ = orbit_point(ex, ey, rx, ry, ang, t * 0.5 + k)
            glow_dot(c, x, y, 8, colr, pk)
            text(c, nm, 300 if k % 2 == 0 else W - 300, 300 + k * 110, 46, colr, "head", "l" if k % 2 == 0 else "r", pk)
        earth(c, ex, ey, 160, t * 0.2, a3)
        text(c, "time becomes distance", W / 2, 1000, 48, CREAM, "head", "c", a3 * P(t, B, "gnss", 0.6, 9.0))
    vignette(c, 0.45)


# ============================== MARS CALLBACK ==============================
def S_mars2(c, t, B, D):
    mars_bg(c, t + 30, night=True)
    rover(c, 1240, 786, 1.0, t)
    hud_corners(c, 0.55)
    typewriter(c, "MISSION LOG // DAY 213", 96, 120, 34, clamp(t / 1.8), TEAL, t=t)
    pill(c, "FICTION", W - 96, 118, 24, NAVY, AMBER, clamp(t / 0.5), align="r")
    if on(t, B, "plan"):
        pk = P(t, B, "plan", 1.0)
        cx, cy = 760, 520
        orbit_ellipse(c, cx, cy, 520, 150, -8, TEAL, 0.45 * pk, 3, dash=[14, 12], phase=-t * 20)
        for k in range(4):
            x, y, d = orbit_point(cx, cy, 520, 150, -8, t * 0.3 + k * math.pi / 2)
            if P(t, B, "plan", 0.5, 1.5 + k * 0.6) > 0:
                satellite(c, x, y, 0.45, 0, pk * P(t, B, "plan", 0.5, 1.5 + k * 0.6))
        text(c, "tuned for Mars's gravity and their own speed", cx, 300, 34, CREAM, "body", "c", P(t, B, "plan", 0.6, 4.5))
    if on(t, B, "right"):
        text_rise(c, "If Einstein was right on Earth…", W / 2, 960, 44, (since(t, B, "right") - 0.1) / 0.7, AMBER, "body")


# ============================== OUTRO / END ==============================
def thumb_path(s=1.0):
    """Original thumbs-up glyph in a 100x100 box centred on (0,0)."""
    p = skia.Path()
    p.addRoundRect(skia.Rect.MakeLTRB(-46, -6, -26, 44), 5, 5)
    p.moveTo(-18, -4); p.lineTo(2, -38); p.quadTo(8, -50, 18, -44); p.quadTo(24, -38, 20, -22)
    p.lineTo(16, -8); p.lineTo(38, -8); p.quadTo(50, -6, 47, 6); p.lineTo(41, 36)
    p.quadTo(38, 46, 28, 46); p.lineTo(-18, 46); p.close()
    m = skia.Matrix(); m.setScale(s, s); p.transform(m)
    return p

def bell_path(s=1.0):
    p = skia.Path()
    p.moveTo(-34, 26); p.lineTo(34, 26); p.lineTo(26, 14); p.lineTo(26, -6)
    p.cubicTo(26, -26, 14, -36, 0, -36); p.cubicTo(-14, -36, -26, -26, -26, -6); p.lineTo(-26, 14); p.close()
    p.addCircle(0, -40, 6); p.addCircle(0, 36, 9)
    m = skia.Matrix(); m.setScale(s, s); p.transform(m)
    return p

def cursor(c, x, y, a=1.0, press=0.0):
    c.save(); c.translate(x, y); sc = 1 - 0.12 * press; c.scale(sc, sc)
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(0, 46); p.lineTo(12, 35); p.lineTo(21, 54); p.lineTo(29, 50)
    p.lineTo(20, 32); p.lineTo(36, 32); p.close()
    c.drawPath(p, paint(NAVY, a, stroke=10, join="round")); c.drawPath(p, paint(CREAM, a))
    c.restore()

def burst(c, x, y, k, color=AMBER, a=1.0, r0=110, r1=170, n=10):
    if k <= 0 or k >= 1: return
    for i in range(n):
        ang = 2 * math.pi * i / n + 0.3
        ra, rb = lerp(r0, r1, eo(k) * 0.6), lerp(r0, r1, eo(k))
        line(c, x + ra * math.cos(ang), y + ra * math.sin(ang), x + rb * math.cos(ang), y + rb * math.sin(ang), color, a * (1 - k), 6)

def S_outro(c, t, B, D):
    bg(c); STARS.draw(c, t, (4, 0), 0.8)
    # soft planet glow at the bottom for depth
    c.drawCircle(W / 2, H + 520, 760, paint(TEAL, 0.10, blur=60))
    a0 = clamp(t / 0.6)
    logo(c, W / 2, 235, 170, a0, spin=t * 12)
    text(c, "COGS & COSMOS", W / 2, 390, 40, CREAM, "head", "c", a0 * 0.9)
    L0 = B["like"][0]; S0 = B["sub"][0]
    t_like, t_sub, t_bell, t_keep = L0 + 3.25, S0 + 0.75, S0 + 3.05, S0 + 6.0
    cy = 700
    # --- like button ---
    lx = W / 2 - 480
    ap = eo((t - 0.2) / 0.5)
    k = clamp((t - t_like) / 0.35)
    pop = 1 + 0.22 * math.sin(math.pi * clamp((t - t_like) / 0.45))
    c.drawCircle(lx, cy, 100 * ap, paint(AMBER if k > 0 else NAVY2, ap))
    c.drawCircle(lx, cy, 100 * ap, paint(AMBER, ap, stroke=5))
    c.save(); c.translate(lx, cy); c.scale(pop * ap, pop * ap)
    c.drawPath(thumb_path(1.25), paint(NAVY if k > 0 else CREAM, ap))
    c.restore()
    burst(c, lx, cy, (t - t_like) / 0.6)
    text(c, "LIKE", lx, cy + 160, 34, AMBER if k > 0 else MIST, "head", "c", ap)
    # --- subscribe button ---
    sp = eo((t - (S0 - 0.3)) / 0.5) if t > S0 - 0.3 else 0.0
    ap2 = max(ap * 0.35, sp)
    done = t >= t_sub
    bw, bh = 520, 136
    pop2 = 1 + 0.10 * math.sin(math.pi * clamp((t - t_sub) / 0.4))
    c.save(); c.translate(W / 2, cy); c.scale(pop2, pop2)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh / 2, bw, bh), bh / 2, bh / 2)
    if done:
        c.drawRRect(r, paint(NAVY3, ap2)); c.drawRRect(r, paint(TEAL, ap2, stroke=5))
        text(c, "SUBSCRIBED", 18, 18, 50, CREAM, "head", "c", ap2)
        tk = clamp((t - t_sub) / 0.35)
        p = skia.Path(); p.moveTo(-205, 0); p.lineTo(-190, 16); p.lineTo(-162, -16)
        c.drawPath(p, paint(TEAL, ap2, stroke=9, dash=[90 * tk + 0.01, 200]))
    else:
        c.drawRRect(r, paint(AMBER, ap2))
        text(c, "SUBSCRIBE", 0, 18, 54, NAVY, "head", "c", ap2)
    c.restore()
    if done: burst(c, W / 2, cy, (t - t_sub) / 0.6, TEAL, 1.0, 150, 230, 14)
    # cursor glides in and clicks
    if S0 - 0.2 < t < t_sub + 0.9:
        mv = eio((t - (S0 - 0.2)) / (t_sub - S0 + 0.1))
        cx_, cy_ = lerp(W / 2 + 420, W / 2 + 120, mv), lerp(cy + 300, cy + 20, mv)
        press = clamp(1 - abs(t - t_sub) / 0.12)
        cursor(c, cx_, cy_, clamp((t_sub + 0.9 - t) / 0.3) * clamp((t - S0 + 0.2) / 0.2), press)
    text(c, "never miss an explainer", W / 2, cy + 160, 34, TEAL if done else MIST, "head", "c", ap2)
    # --- bell ---
    bx = W / 2 + 480
    bp = max(ap * 0.35, eo((t - (S0 + 1.8)) / 0.5) if t > S0 + 1.8 else 0.0)
    kb = t >= t_bell
    c.drawCircle(bx, cy, 100, paint(AMBER if kb else NAVY2, bp))
    c.drawCircle(bx, cy, 100, paint(AMBER, bp, stroke=5))
    sw = math.sin((t - t_bell) * 22) * 18 * math.exp(-(t - t_bell) * 2.2) if kb else 0.0
    c.save(); c.translate(bx, cy - 40); c.rotate(sw); c.translate(0, 40)
    c.drawPath(bell_path(1.45), paint(NAVY if kb else CREAM, bp))
    c.restore()
    if kb:
        for j in range(2):
            ph = ((t - t_bell) * 1.3 + j * 0.5) % 1.0
            if t - t_bell < 2.2:
                for sgn in (-1, 1):
                    pth = skia.Path(); rr = 120 + 60 * ph
                    pth.addArc(skia.Rect.MakeLTRB(bx - rr, cy - rr, bx + rr, cy + rr), (-90 + sgn * 55) - 20, 40)
                    c.drawPath(pth, paint(AMBER, (1 - ph) * 0.9, stroke=6))
    text(c, "ALL NOTIFICATIONS", bx, cy + 160, 34, AMBER if kb else MIST, "head", "c", bp)
    # --- sign-off ---
    if t >= t_keep - 0.1:
        text_rise(c, "Keep exploring.", W / 2, 520, 76, (t - t_keep + 0.1) / 0.6, AMBER)
    vignette(c, 0.45)

def S_end(c, t, B, D):
    bg(c); STARS.draw(c, t + 10, (4, 0), 0.9)
    logo(c, 300, 300, 160, 1.0, spin=t * 8)
    text(c, "Keep exploring", 120, 520, 84, CREAM, "head", "l")
    text(c, "One new explainer every week,", 120, 590, 36, MIST, "body", "l")
    text(c, "from tiny cogs to the whole cosmos.", 120, 640, 36, MIST, "body", "l")
    ring(c, 230, 840, 105, TEAL, 0.25, 3, dash=[12, 10])
    rrect(c, W - 120 - 720, 135, 720, 405, 16, AMBER, 0.18, stroke=3)
    rrect(c, W - 120 - 720, 580, 720, 405, 16, AMBER, 0.18, stroke=3)
    vignette(c, 0.4)


SCENES = {"mars": S_mars, "title": S_title, "hook": S_hook, "b1": S_b1, "b2": S_b2, "b3": S_b3,
          "tw": S_tw, "ans": S_ans, "mars2": S_mars2, "outro": S_outro, "end": S_end}
