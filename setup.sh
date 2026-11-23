#!/usr/bin/env bash
# One-time setup in a fresh session: Python deps + Kokoro voice model (Apache-2.0, from GitHub releases).
set -e
cd "$(dirname "$0")"
pip install --quiet --break-system-packages skia-python kokoro-onnx soundfile scipy numpy pillow fonttools 2>/dev/null \
  || pip install --quiet skia-python kokoro-onnx soundfile scipy numpy pillow fonttools
mkdir -p models
for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
  [ -s "models/$f" ] || curl -sSL -o "models/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg not found"
python3 -c "import skia, kokoro_onnx, soundfile, scipy; print('engine ready')"
