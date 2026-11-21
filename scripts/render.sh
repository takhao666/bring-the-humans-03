#!/usr/bin/env bash
# Render the bring-the-humans-03 TikTok ad (1080x1920, 18 s) from the
# scene stills scripts/build_video.py makes.
#
# Pipeline (all in this session, ffmpeg only):
#   1. Scene A 5 s -> Scene B 6 s -> Scene C 7 s, 0.5 s crossfades.
#   2. The press pack brand badge (assets/badge-9x16.png, 1080x1920,
#      used as-is) overlaid from the first frame until the end card.
#   3. The press pack referral end card (assets/card-9x16-transparent.webm,
#      VP9 with alpha, 2.5 s) over the last 2.5 s, with the clip blurred
#      (sigma 28) and desaturated under it, exactly per
#      https://make.fun/press/llms.txt -- the referral code hvn9m3q0 is
#      typed into the field in Inter Bold 62 px, ink #191419, once the
#      field comes to rest (1.433 s into the card).
#
# Run:  bash scripts/render.sh
# Out:  ad.mp4  (1080x1920, 30 fps, H.264 + silent AAC)
set -euo pipefail
cd "$(dirname "$0")/.."

CODE="hvn9m3q0"
FONT="assets/Inter-Bold.otf"
CARD="assets/card-9x16-transparent.webm"
BADGE="assets/badge-9x16.png"
W=1080; H=1920; LEN=2.5; REST=1.433
CX=210; CY=1232; CW=5; CH=78; MID=1271; SIZE=62
TOTAL=18
T=$(python3 -c "print($TOTAL - $LEN)")

ffmpeg -y -v error \
  -loop 1 -t 5.5 -i build/scenes/scene-a.png \
  -loop 1 -t 6.5 -i build/scenes/scene-b.png \
  -loop 1 -t 7 -i build/scenes/scene-c.png \
  -c:v libvpx-vp9 -i "$CARD" \
  -i "$BADGE" \
  -f lavfi -t $TOTAL -i anullsrc=r=44100:cl=stereo \
  -filter_complex "\
[0:v]fps=30,format=yuv420p,settb=AVTB[a]; \
[1:v]fps=30,format=yuv420p,settb=AVTB[b]; \
[2:v]fps=30,format=yuv420p,settb=AVTB[c]; \
[a][b]xfade=transition=fade:duration=0.5:offset=5.0[x1]; \
[x1][c]xfade=transition=fade:duration=0.5:offset=11.0[clip]; \
[clip]split[base][soft]; \
[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=$T:d=0.8:alpha=1[soft]; \
[base][soft]overlay[bg]; \
[bg][4:v]overlay=enable='lt(t,$T)'[badged]; \
[3:v]format=yuva420p,setpts=PTS-STARTPTS+$T/TB[card]; \
[badged][card]overlay=eof_action=pass, \
drawbox=x=$CX-2:y=$CY-2:w=$CW+4:h=$CH+4:color=white:t=fill:enable='gte(t,$T+$REST)', \
drawtext=fontfile=$FONT:text=$CODE:fontsize=$SIZE:fontcolor=0x191419:x=$CX:y=$MID-(ascent-descent)/2:enable='gte(t,$T+$REST)'[v]" \
  -map '[v]' -map 5:a -c:v libx264 -pix_fmt yuv420p -r 30 -crf 18 \
  -c:a aac -b:a 128k -movflags +faststart -t $TOTAL ad.mp4

ffprobe -v error -show_entries stream=codec_name,width,height,duration,r_frame_rate \
  -show_entries format=duration,size -of default=noprint_wrappers=1 ad.mp4
