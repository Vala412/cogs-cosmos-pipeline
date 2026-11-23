"""Narrate every line of EP/script.py with Kokoro (kept files are reused). Run with EP=<episode dir>.
Env VOICE (default af_heart), SPEED (default 0.96)."""
import json, os, sys, importlib.util
import soundfile as sf
from kokoro_onnx import Kokoro
ENGINE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(ENGINE)
EP = os.path.abspath(os.environ.get("EP", os.getcwd()))
spec = importlib.util.spec_from_file_location("ep_script", os.path.join(EP, "script.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); LINES = mod.LINES
VOICE = os.environ.get("VOICE", getattr(mod, "VOICE", "af_heart")); SPEED = float(os.environ.get("SPEED", getattr(mod, "SPEED", 0.96)))
k = Kokoro(f"{ROOT}/models/kokoro-v1.0.int8.onnx", f"{ROOT}/models/voices-v1.0.bin")
os.makedirs(f"{EP}/audio/lines", exist_ok=True)
meta = []
for i, (scene, beat, say, cap, pause) in enumerate(LINES):
    path = f"{EP}/audio/lines/{i:03d}.wav"
    dur = 0.0
    if say:
        if not os.path.exists(path):
            s, sr = k.create(say, voice=VOICE, speed=SPEED, lang="en-us")
            sf.write(path + ".tmp.wav", s, sr); os.rename(path + ".tmp.wav", path)
        info = sf.info(path); dur = info.frames / info.samplerate
    meta.append({"i": i, "scene": scene, "beat": beat, "dur": round(dur, 3), "pause": pause})
    print(i, scene, beat, round(dur, 2), flush=True)
json.dump(meta, open(f"{EP}/audio/lines.json", "w"), indent=1)
print("done")
