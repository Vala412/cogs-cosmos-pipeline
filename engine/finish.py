"""Join rendered scenes, master the audio and mux the final video.
Run with EP=<episode dir> after render.py scenes + mix.py.

  python3 engine/finish.py NAME.mp4                 # CRF 18 master (long videos)
  python3 engine/finish.py NAME.mp4 --max-mb 3.6    # two-pass to a size cap (Shorts uploaded through Chrome: 3.8 MB limit)
"""
import os, sys, glob, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import EP

def run(cmd):
    print(" ".join(cmd)[:160], flush=True)
    subprocess.run(cmd, check=True)

def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])

def main():
    name = sys.argv[1]
    max_mb = float(sys.argv[sys.argv.index("--max-mb") + 1]) if "--max-mb" in sys.argv else None
    out_dir = f"{EP}/out"; scenes = sorted(glob.glob(f"{out_dir}/scenes/*.mp4"))
    assert scenes, "no rendered scenes"
    with open(f"{out_dir}/concat.txt", "w") as f:
        for s in scenes: f.write(f"file '{s}'\n")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out_dir}/concat.txt",
         "-c", "copy", f"{out_dir}/video_only.tmp.mp4"]); os.replace(f"{out_dir}/video_only.tmp.mp4", f"{out_dir}/video_only.mp4")
    # master: gentle compression + limiter, lands near -14 LUFS for typical voice-led mixes
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{out_dir}/mix_pre.wav", "-af",
         "acompressor=threshold=-22dB:ratio=3:attack=8:release=150:makeup=1,volume=11.2dB,alimiter=limit=0.82:attack=3:release=60:level=disabled",
         "-ar", "48000", "-c:a", "pcm_s24le", f"{out_dir}/mix_c.wav"])
    final = f"{out_dir}/{name}"; tmp = final[:-4] + ".tmp.mp4"
    if max_mb is None:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{out_dir}/video_only.mp4", "-i", f"{out_dir}/mix_c.wav",
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
             "-movflags", "+faststart", tmp])
    else:
        d = dur(f"{out_dir}/video_only.mp4"); abr = 96
        vbr = int((max_mb * 8e6 * 0.92) / d / 1000 - abr)  # decimal MB, 8% headroom for container + rate drift
        assert vbr > 250, f"too long for {max_mb} MB ({vbr} kbps video)"
        common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vbr}k", "-maxrate", f"{int(vbr * 1.6)}k", "-bufsize", f"{vbr * 2}k", "-bf", "2", "-pix_fmt", "yuv420p", "-r", "30"]
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{out_dir}/video_only.mp4", "-map", "0:v", *common, "-pass", "1",
             "-passlogfile", f"{out_dir}/x264", "-an", "-f", "mp4", "/dev/null"])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{out_dir}/video_only.mp4", "-i", f"{out_dir}/mix_c.wav",
             "-map", "0:v", "-map", "1:a", *common, "-pass", "2", "-passlogfile", f"{out_dir}/x264",
             "-c:a", "aac", "-b:a", f"{abr}k", "-ar", "48000", "-shortest", "-movflags", "+faststart", tmp])
    os.replace(tmp, final)
    if max_mb is not None:
        assert os.path.getsize(final) <= max_mb * 1e6, f"{final} is {os.path.getsize(final) / 1e6:.2f} MB, over the {max_mb} MB cap"
    lufs = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", final, "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    i_line = [l.strip() for l in lufs.splitlines() if l.strip().startswith("I:")][-1:]
    print(f"{final}: {os.path.getsize(final) / 1e6:.2f} MB, {dur(final):.2f} s, loudness {i_line}")

if __name__ == "__main__":
    main()
