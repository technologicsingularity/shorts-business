#!/bin/bash
# Create multi-scene video with one background using zoom/pan effects

ffmpeg -i /data/.openclaw/workspace/smoke_detector_bg.png -vf "
zoompan=z='min(zoom+0.0015,1.5)':d=750:s=1280x720:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',
fade=t=out:st=9:d=1
" -t 10 -c:v libx264 -pix_fmt yuv420p /data/.openclaw/workspace/scene1.mp4

ffmpeg -i /data/.openclaw/workspace/smoke_detector_bg.png -vf "
colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3,
zoompan=z='1.5':d=750:s=1280x720:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',
fade=t=in:st=0:d=1,fade=t=out:st=9:d=1
" -t 10 -c:v libx264 -pix_fmt yuv420p /data/.openclaw/workspace/scene2.mp4

ffmpeg -i /data/.openclaw/workspace/smoke_detector_bg.png -vf "
colorbalance=bs=.3,
zoompan=z='if(between(time,0,5),1.5,1.5-0.1*(time-5))':d=750:s=1280x720:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',
fade=t=in:st=0:d=1,fade=t=out:st=14:d=1
" -t 15 -c:v libx264 -pix_fmt yuv420p /data/.openclaw/workspace/scene3.mp4

ffmpeg -i /data/.openclaw/workspace/smoke_detector_bg.png -vf "
egamma=.8,
zoompan=z='1.0':d=750:s=1280x720:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',
fade=t=in:st=0:d=1,fade=t=out:st=14:d=1
" -t 15 -c:v libx264 -pix_fmt yuv420p /data/.openclaw/workspace/scene4.mp4

echo "Scenes created!"
ls -lh /data/.openclaw/workspace/scene*.mp4
