#!/usr/bin/env python3
"""
Video creation script for YouTube Shorts (9:16 vertical format)
Ensures video length = audio length, optimized for Shorts
"""

import subprocess
import sys
import os

def get_audio_duration(audio_file):
    """Get audio duration in seconds."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', audio_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def create_short(background, face_video, audio_file, output_file, face_offset=100):
    """
    Create YouTube Short (9:16 vertical) with validation.
    
    Args:
        background: Path to 9:16 background image
        face_video: Path to face overlay video
        audio_file: Path to audio file
        output_file: Output path
        face_offset: Pixels from right edge (default 100 for vertical)
    """
    
    # Get audio duration
    audio_duration = get_audio_duration(audio_file)
    print(f"Audio duration: {audio_duration:.2f} seconds")
    
    # Validate for Shorts
    if audio_duration < 30:
        print(f"WARNING: Audio is only {audio_duration:.1f}s - might be too short")
    elif audio_duration > 90:
        print(f"WARNING: Audio is {audio_duration:.1f}s - might be too long for Shorts")
    
    # Build ffmpeg command for 9:16 vertical Shorts
    # Resolution: 1080x1920 (9:16)
    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', background,
        '-stream_loop', '-1', '-i', face_video,
        '-i', audio_file,
        '-filter_complex',
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
        f"zoompan=z='if(lte(time,{audio_duration/2}),1+0.015*time,1.15-0.015*(time-{audio_duration/2}))':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920[bg];"
        f"[1:v]scale=200:200[face];"  # Slightly larger face for vertical
        f"[bg][face]overlay=x=W-w-{face_offset}:y=H-h-150",  # Higher up for vertical
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-t', str(audio_duration),
        output_file
    ]
    
    print(f"Creating Short (9:16, duration locked to {audio_duration:.2f}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Video creation failed")
        print(result.stderr[-500:])  # Last 500 chars of error
        return False
    
    # Verify output
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        print(f"ERROR: Output file missing or empty")
        return False
    
    # Verify dimensions
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 
           'stream=width,height', '-of', 'csv=s=x:p=0', output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    dimensions = result.stdout.strip()
    print(f"Output dimensions: {dimensions}")
    
    if dimensions != "1080x1920":
        print(f"WARNING: Expected 1080x1920, got {dimensions}")
    
    output_duration = get_audio_duration(output_file)
    print(f"Output duration: {output_duration:.2f}s")
    
    if abs(output_duration - audio_duration) > 1.0:
        print(f"ERROR: Duration mismatch!")
        return False
    
    print(f"✅ Short created successfully: {output_file}")
    print(f"   Dimensions: {dimensions}")
    print(f"   Duration: {output_duration:.2f}s")
    print(f"   File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    
    return True

def create_standard_video(background, face_video, audio_file, output_file, face_offset=80):
    """Create standard 16:9 video for music/long-form content."""
    
    audio_duration = get_audio_duration(audio_file)
    print(f"Audio duration: {audio_duration:.2f} seconds")
    
    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', background,
        '-stream_loop', '-1', '-i', face_video,
        '-i', audio_file,
        '-filter_complex',
        f"[0:v]zoompan=z='if(lte(time,{audio_duration/2}),1+0.02*time,1.2-0.02*(time-{audio_duration/2}))':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080[bg];"
        f"[1:v]scale=180:180[face];"
        f"[bg][face]overlay=x=W-w-{face_offset}:y=H-h-20",
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-t', str(audio_duration),
        output_file
    ]
    
    print(f"Creating standard video (16:9, duration locked to {audio_duration:.2f}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Video creation failed")
        return False
    
    output_duration = get_audio_duration(output_file)
    print(f"✅ Video created: {output_file} ({output_duration:.2f}s)")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: python3 create_video.py <type> <background> <face> <audio> <output>")
        print("  type: 'shorts' (9:16) or 'standard' (16:9)")
        sys.exit(1)
    
    video_type = sys.argv[1]
    background = sys.argv[2]
    face = sys.argv[3]
    audio = sys.argv[4]
    output = sys.argv[5]
    
    if video_type == 'shorts':
        success = create_short(background, face, audio, output)
    else:
        success = create_standard_video(background, face, audio, output)
    
    sys.exit(0 if success else 1)
