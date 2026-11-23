"""Build the sound track for EP: narration + original synthesized music + SFX, ducked -> EP/out/mix_pre.wav.
Music follows MOODS in EP/script.py: {scene_key: "calm"|"tense"|"drone"|"bright"}; missing scenes are "calm".
Optional STING = scene key that gets a title sting at its start; TWIST = scene key that gets a low boom."""
import json, math, os, sys
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, sosfilt, butter, fftconvolve, lfilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import build_timeline, EP
import importlib.util
_spec = importlib.util.spec_from_file_location("ep_script", os.path.join(EP, "script.py"))
_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
MOODS = getattr(_mod, "MOODS", {}); STING = getattr(_mod, "STING", None); TWIST = getattr(_mod, "TWIST", None)
HERE = EP

SR = 48000
rng = np.random.default_rng(7)
items, scenes, total = build_timeline()
N = int(math.ceil(total * SR)) + SR
SC = {s["key"]: s for s in scenes}

def at(t): return int(round(t * SR))
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def db(x): return 10 ** (x / 20)

# ---------------- narration ----------------
voice = np.zeros(N, np.float32)
for it in items:
    if not it["say"]: continue
    w, sr = sf.read(f"{HERE}/audio/lines/{it['i']:03d}.wav", dtype="float32")
    if w.ndim > 1: w = w.mean(1)
    w = resample_poly(w, SR, sr).astype(np.float32)
    s = at(it["start"]); voice[s:s + len(w)] += w[: max(0, N - s)]
# gentle presence lift + high-pass to clean rumble
voice = sosfilt(butter(2, 80, "hp", fs=SR, output="sos"), voice).astype(np.float32)
pk = np.max(np.abs(voice)); voice *= db(-3) / pk

# ---------------- music helpers ----------------
def env_ar(n, a, r):
    e = np.ones(n, np.float32)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na: e[:na] = np.linspace(0, 1, na) ** 2
    if nr: e[n - nr:] *= np.linspace(1, 0, nr) ** 2
    return e

def pad_note(f, dur, a=1.2, r=1.8, bright=0.35):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    for det in (-0.004, 0.0, 0.0041):
        ff = f * (1 + det); ph = rng.uniform(0, 6.28)
        for h in range(1, 6):
            if ff * h > 6000: break
            out += (np.sin(2 * np.pi * ff * h * t + ph * h) * (math.exp(-h * (1 - bright) * 1.1) / h)).astype(np.float32)
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.13 * t + rng.uniform(0, 6))
    return out * env_ar(n, a, r) * lfo.astype(np.float32) / 6

def pluck(f, dur=1.6, decay=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    e = np.exp(-t / decay) * np.minimum(1, t / 0.004)
    return (s * e).astype(np.float32)

def add(buf, x, s):
    s = int(s)
    if s >= len(buf): return
    if s < 0: x = x[-s:]; s = 0
    e = min(len(buf), s + len(x)); buf[s:e] += x[: e - s]

def section_gain(t0, t1, fin=1.5, fout=1.5):
    g = np.zeros(N, np.float32); a, b = at(t0), at(t1)
    g[a:b] = 1
    fi, fo = int(fin * SR), int(fout * SR)
    g[a:a + fi] = np.linspace(0, 1, fi)[: len(g[a:a + fi])]
    if b - fo > a: g[b - fo:b] = np.linspace(1, 0, fo)[: len(g[b - fo:b])]
    return g

pads = np.zeros(N, np.float32); arps = np.zeros(N, np.float32); low = np.zeros(N, np.float32)

# Chord sets (MIDI). Bright main loop in D major, tense loop in B minor, Mars drones.
MAIN = [[50, 57, 62, 66, 73], [47, 54, 62, 66, 69], [43, 50, 59, 62, 66], [45, 52, 57, 59, 64]]   # Dmaj7 Bm7 Gmaj7 Asus2
TENSE = [[47, 54, 59, 62, 66], [43, 50, 55, 59, 62], [40, 47, 55, 59, 64], [42, 49, 54, 58, 61]]  # Bm G Em F#
BPM = 96; EIGHTH = 60 / BPM / 2; CH = 16 * EIGHTH   # one chord per two bars (5 s)

def chord_loop(t0, t1, chords, arp=True, arp_from=None, arp_gain=0.16, pad_gain=1.0, oct_up=12):
    t = t0; k = 0
    while t < t1:
        ch = chords[k % len(chords)]
        d = min(CH + 1.8, t1 - t + 1.8)
        for m in ch: add(pads, pad_gain * pad_note(midi(m), d), at(t))
        if arp and (arp_from is None or t >= arp_from - 0.01):
            pat = [ch[1] + oct_up, ch[2] + oct_up, ch[3] + oct_up, ch[4] + oct_up, ch[3] + oct_up, ch[2] + oct_up, ch[4] + oct_up, ch[2] + oct_up]
            for j in range(16):
                tt = t + j * EIGHTH
                if tt >= t1: break
                g = arp_gain * (1.0 if j % 4 == 0 else 0.7)
                add(arps, g * pluck(midi(pat[j % 8]), 1.2, 0.35), at(tt))
        t += CH; k += 1

# Mars: dark drone + wind
def drone(t0, t1, notes, g=1.0):
    for m in notes: add(pads, g * pad_note(midi(m), t1 - t0 + 2, a=3.0, r=3.0, bright=0.15), at(t0))

def wind(t0, t1, g=0.5):
    n = at(t1) - at(t0); x = rng.standard_normal(n).astype(np.float32)
    x = sosfilt(butter(2, [180, 900], "bp", fs=SR, output="sos"), x)
    tt = np.arange(n) / SR
    sw = 0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * tt) * np.sin(2 * np.pi * 0.023 * tt + 1)
    add(low, (g * x * sw * env_ar(n, 2.5, 2.5)).astype(np.float32), at(t0))

# ---- music by mood, scene by scene ----
BRIGHT = [[50, 57, 62, 66, 69], [55, 62, 67, 71, 74], [52, 59, 64, 67, 71], [57, 64, 69, 73, 76]]  # D G Em A (higher, lighter)
for sc in scenes:
    mood = MOODS.get(sc["key"], "calm"); s0, s1 = sc["start"], sc["end"]
    if s1 - s0 < 0.5: continue
    if mood == "drone":
        drone(s0, s1, [38, 45, 50, 53], 1.0); wind(s0, s1 + 0.6, 0.7)
    elif mood == "tense":
        chord_loop(s0, s1, TENSE, arp=True, arp_gain=0.12)
        t_ = s0
        while t_ < s1: add(low, 0.18 * pluck(midi(35), 0.4, 0.18), at(t_)); t_ += 2 * EIGHTH
    elif mood == "bright":
        chord_loop(s0, s1, BRIGHT, arp=True, arp_gain=0.14)
    else:
        chord_loop(s0, s1, MAIN, arp=True, arp_gain=0.15)
if STING and STING in SC:
    ts = SC[STING]["start"]
    n = int(1.4 * SR); x = rng.standard_normal(n).astype(np.float32)
    x = sosfilt(butter(2, 2500, "hp", fs=SR, output="sos"), x) * (np.linspace(0, 1, n) ** 3)
    add(low, 0.25 * x.astype(np.float32), at(ts - 1.3))
    for m in [50, 57, 62, 66, 69, 76]: add(arps, 0.11 * pluck(midi(m), 3.0, 1.1), at(ts + 0.1))
    add(low, 0.5 * pluck(36.7, 2.0, 0.6), at(ts + 0.1))
if TWIST and TWIST in SC:
    bn = int(1.8 * SR); bt = np.arange(bn) / SR
    boom = np.sin(2 * np.pi * (55 * np.exp(-bt * 1.2) + 30) * bt) * np.exp(-bt / 0.6)
    add(low, 0.55 * boom.astype(np.float32), at(SC[TWIST]["start"] - 0.05))

# ---------------- SFX ----------------
sfx = np.zeros(N, np.float32)
def whoosh(t, dur=0.9, g=0.22):
    n = int(dur * SR); x = rng.standard_normal(n).astype(np.float32)
    y = np.zeros(n, np.float32); segs = 24
    for k in range(segs):
        a, b = k * n // segs, (k + 1) * n // segs
        fc = 300 + 3200 * math.sin(math.pi * (k + 0.5) / segs)
        sos = butter(2, [fc * 0.6, min(fc * 1.6, 20000)], "bp", fs=SR, output="sos")
        y[a:b] = sosfilt(sos, x[a:b])
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    add(sfx, g * y * e, at(t - dur * 0.55))

def pop(t, g=0.10, f=880):
    n = int(0.09 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * (1 - 0.35 * tt / 0.09) * tt) * np.exp(-tt / 0.025)
    add(sfx, (g * s).astype(np.float32), at(t))

for sc in scenes[1:]:
    if sc["key"] == STING: continue
    whoosh(sc["start"] - 0.15)
for it in items:
    sc = SC[it["scene"]]
    first = min(sc["beats"].values())[0] + sc["start"]
    if abs(it["start"] - first) < 1e-6 or MOODS.get(it["scene"]) == "drone": continue
    if it["start"] == sc["start"] + sc["beats"][it["beat"]][0]:
        pop(it["start"] - 0.05, 0.06, 760 + 180 * (it["i"] % 3))

# ---------------- reverb + stereo ----------------
def ir(seconds, seed):
    r = np.random.default_rng(seed); n = int(seconds * SR)
    t = np.arange(n) / SR
    h = r.standard_normal(n) * np.exp(-t / (seconds / 6.5))
    h = sosfilt(butter(1, 5000, "lp", fs=SR, output="sos"), h)
    return (h / np.sqrt(np.sum(h ** 2))).astype(np.float32)

music_mono = sosfilt(butter(2, 2600, "lp", fs=SR, output="sos"), pads) + arps
L = music_mono * 0.7 + fftconvolve(music_mono, ir(2.8, 1), "full")[:N] * 0.55
R = music_mono * 0.7 + fftconvolve(music_mono, ir(2.8, 2), "full")[:N] * 0.55
low_r = low + fftconvolve(low, ir(1.6, 3), "full")[:N] * 0.3
L += low_r; R += low_r
sfxL = sfx + fftconvolve(sfx, ir(1.2, 4), "full")[:N] * 0.25
sfxR = sfx + fftconvolve(sfx, ir(1.2, 5), "full")[:N] * 0.25

# end fade
fo = at(total) ; fl = int(3.5 * SR)
fade = np.ones(N, np.float32); fade[fo - fl:fo] = np.linspace(1, 0, fl); fade[fo:] = 0
L *= fade; R *= fade

# ---------------- ducking ----------------
a = np.abs(voice)
att, rel = math.exp(-1 / (0.03 * SR)), math.exp(-1 / (0.45 * SR))
# fast envelope: block RMS then smooth
blk = 480; nb = N // blk
rms = np.sqrt(np.mean(voice[: nb * blk].reshape(nb, blk) ** 2, axis=1))
envb = np.zeros(nb); e = 0.0
for k in range(nb):
    v = rms[k]; c = 0.5 if v > e else 0.06
    e = e + c * (v - e); envb[k] = e
env = np.repeat(envb, blk); env = np.pad(env, (0, N - len(env)), mode="edge")
duck = 1 - 0.6 * np.clip(env / 0.05, 0, 1)

mrms = np.sqrt(np.mean(((L + R) / 2)[: at(total)] ** 2)) + 1e-9
mg = db(-31) / mrms  # music bed level relative to full scale before ducking
L = L * mg * duck; R = R * mg * duck
sg = db(-6)
outL = voice + L + sfxL * sg
outR = voice + R + sfxR * sg
out = np.stack([outL, outR], 1)[: at(total) + int(0.2 * SR)]
out /= max(1.0, np.max(np.abs(out)) / db(-1.5))
os.makedirs(f"{HERE}/out", exist_ok=True)
sf.write(f"{HERE}/out/mix_pre.wav", out.astype(np.float32), SR, subtype="FLOAT")
print("mix", out.shape[0] / SR, "s")
