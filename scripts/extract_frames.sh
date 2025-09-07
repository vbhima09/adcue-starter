#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/frames
for f in data/raw_videos/*.mp4; do
  name=$(basename "${f%.mp4}")
  mkdir -p "data/frames/$name"
  # 1 fps frames
  ffmpeg -y -i "$f" -vf fps=1 "data/frames/$name/frame_%04d.jpg"
done