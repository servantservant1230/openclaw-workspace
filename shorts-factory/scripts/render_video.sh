#!/bin/zsh
set -euo pipefail
BASE="/Volumes/WORK_SSD/workspace/shorts-factory"
IDX="${1:-1}"
BG="${2:-$BASE/assets/bg.mp4}"
AUDIO="${3:-$BASE/assets/voice_topic_${IDX}.m4a}"
SRT="$BASE/subtitles/topic_${IDX}.srt"
OUT="$BASE/outputs/video_topic_${IDX}.mp4"

if [[ ! -f "$BG" ]]; then
  echo "missing bg video: $BG" >&2; exit 1
fi
if [[ ! -f "$AUDIO" ]]; then
  echo "missing voice audio: $AUDIO" >&2; exit 1
fi
if [[ ! -f "$SRT" ]]; then
  echo "missing subtitle: $SRT" >&2; exit 1
fi

ffmpeg -y -stream_loop -1 -i "$BG" -i "$AUDIO" \
  -vf "subtitles='$SRT':force_style='Fontsize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40'" \
  -map 0:v:0 -map 1:a:0 -shortest \
  -c:v libx264 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k "$OUT"

echo "rendered: $OUT"
