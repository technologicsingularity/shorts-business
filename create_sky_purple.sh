#!/bin/bash
cd /data/.openclaw/workspace
rm -f step1.mp4 sky_purple_final.mp4

# Create step 1: Background video with audio
echo "Creating background video..."
ffmpeg -y -loop 1 -i sky_purple_9x16.png -i audio/sky_purple_audio.mp3 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a aac -shortest step1.mp4

if [ $? -ne 0 ]; then
  echo "ERROR: Step 1 failed"
  exit 1
fi

echo "Step 1 complete. Verifying..."
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 step1.mp4

# Create step 2: Overlay face
echo "Creating final video with face overlay..."
ffmpeg -y -i step1.mp4 -stream_loop -1 -i alita_face_loop_final.mp4 \
  -filter_complex "[0:v][1:v]overlay=x=W-w-80:y=H-h-150:shortest=1" \
  -c:v libx264 -pix_fmt yuv420p -c:a copy sky_purple_final.mp4

if [ $? -ne 0 ]; then
  echo "ERROR: Step 2 failed"
  exit 1
fi

echo "Final video created!"
ls -la sky_purple_final.mp4
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 sky_purple_final.mp4
