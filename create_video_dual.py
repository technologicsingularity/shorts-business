#!/usr/bin/env python3
"""
Video creation script for YouTube Shorts - DUAL IMAGE VERSION
Shows first image for 12s, then switches to second image for retention boost
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

def validate_inputs(bg1, bg2, face, audio):
    """Validate all input files exist and are correct types."""
    errors = []
    
    for path, name in [(bg1, "Background 1"), (bg2, "Background 2"), (face, "Face overlay")]:
        if not os.path.exists(path):
            errors.append(f"❌ {name} not found: {path}")
        else:
            size_mb = os.path.getsize(path) / (1024*1024)
            print(f"✓ {name}: {path} ({size_mb:.2f} MB)")
    
    if not os.path.exists(audio):
        errors.append(f"❌ Audio not found: {audio}")
    else:
        duration = get_audio_duration(audio)
        print(f"✓ Audio: {audio} ({duration:.1f}s)")
        if duration < 20:
            errors.append(f"⚠️ Audio very short ({duration:.1f}s)")
        elif duration > 90:
            errors.append(f"⚠️ Audio very long ({duration:.1f}s)")
    
    return errors

def create_dual_image_short(bg1, bg2, face_video, audio_file, output_file, 
                             switch_time=12, face_offset=100, dry_run=False):
    """
    Create YouTube Short with TWO background images.
    
    Args:
        bg1: First background image (shown 0 to switch_time)
        bg2: Second background image (shown switch_time to end)
        face_video: Face overlay video
        audio_file: Audio track
        output_file: Output path
        switch_time: When to switch images (default 12 seconds)
        face_offset: Pixels from right edge
        dry_run: If True, only show command without executing
    """
    
    # Validate inputs
    print("\n=== INPUT VALIDATION ===")
    errors = validate_inputs(bg1, bg2, face_video, audio_file)
    if errors:
        for e in errors:
            print(e)
        if any("❌" in e for e in errors):
            return False
    
    # Get audio duration
    audio_duration = get_audio_duration(audio_file)
    print(f"\nAudio duration: {audio_duration:.2f}s")
    print(f"Image switch at: {switch_time}s")
    print(f"Image 2 duration: {audio_duration - switch_time:.2f}s")
    
    if audio_duration <= switch_time:
        print(f"⚠️ Audio ({audio_duration:.1f}s) shorter than switch time ({switch_time}s)")
        print("Falling back to single image mode...")
        return create_single_image_short(bg1, face_video, audio_file, output_file, face_offset, dry_run)
    
    # Build ffmpeg command for dual-image Short
    # Strategy: 
    # 1. Loop both backgrounds
    # 2. Trim bg1 to 0-12s, trim bg2 to 12s-end
    # 3. Concatenate them
    # 4. Apply zoompan to the concatenated result
    # 5. Overlay face
    
    # Fixed filter chain - scale to consistent resolution BEFORE concat
    # Both inputs scaled to 1080x1920 first, then trimmed, then concatenated
    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', bg1,
        '-stream_loop', '-1', '-i', bg2,
        '-stream_loop', '-1', '-i', face_video,
        '-i', audio_file,
        '-filter_complex',
        # Scale both backgrounds to 1080x1920 FIRST, then trim, then concat
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,trim=start=0:end={switch_time},setpts=PTS-STARTPTS[bg1];"
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,trim=start=0:end={audio_duration-switch_time},setpts=PTS-STARTPTS[bg2];"
        f"[bg1][bg2]concat=n=2:v=1:a=0[bg_concat];"
        # Apply zoompan to the concatenated result
        f"[bg_concat]zoompan=z='if(lte(time,{audio_duration/2}),1+0.015*time,1.15-0.015*(time-{audio_duration/2}))':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920[bg];"
        # Scale face
        f"[2:v]scale=200:200[face];"
        # Overlay face on background
        f"[bg][face]overlay=x=W-w-{face_offset}:y=H-h-150:shortest=1",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest',
        '-t', str(audio_duration),
        output_file
    ]
    
    print(f"\n=== RENDERING ===")
    print(f"Output: {output_file}")
    print(f"Switch at: {switch_time}s")
    
    if dry_run:
        print("\n[DRY RUN - Command only]")
        print(' '.join(cmd[:15]) + " ... [filter_complex trimmed] ...")
        return True
    
    print("Rendering... (this may take a minute)")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ ERROR: Video creation failed")
        print(result.stderr[-1000:])
        return False
    
    # Verify output
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        print(f"❌ ERROR: Output file missing or empty")
        return False
    
    # Verify dimensions and duration
    cmd_dim = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 
               'stream=width,height', '-of', 'csv=s=x:p=0', output_file]
    result_dim = subprocess.run(cmd_dim, capture_output=True, text=True)
    dimensions = result_dim.stdout.strip()
    
    output_duration = get_audio_duration(output_file)
    
    print(f"\n=== OUTPUT VERIFICATION ===")
    print(f"✓ Created: {output_file}")
    print(f"✓ Dimensions: {dimensions} (expected: 1080x1920)")
    print(f"✓ Duration: {output_duration:.2f}s (expected: {audio_duration:.2f}s)")
    print(f"✓ File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    
    if dimensions != "1080x1920":
        print(f"⚠️ WARNING: Dimensions mismatch!")
    
    if abs(output_duration - audio_duration) > 1.0:
        print(f"⚠️ WARNING: Duration mismatch!")
        return False
    
    print(f"\n✅ SUCCESS: Dual-image Short created!")
    print(f"   Image 1: 0-{switch_time}s")
    print(f"   Image 2: {switch_time}s-{output_duration:.1f}s")
    
    return True

def create_single_image_short(background, face_video, audio_file, output_file, 
                               face_offset=100, dry_run=False):
    """Fallback: Create single-image Short (original behavior)."""
    
    audio_duration = get_audio_duration(audio_file)
    
    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', background,
        '-stream_loop', '-1', '-i', face_video,
        '-i', audio_file,
        '-filter_complex',
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
        f"zoompan=z='if(lte(time,{audio_duration/2}),1+0.015*time,1.15-0.015*(time-{audio_duration/2}))':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920[bg];"
        f"[1:v]scale=200:200[face];"
        f"[bg][face]overlay=x=W-w-{face_offset}:y=H-h-150",
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-t', str(audio_duration),
        output_file
    ]
    
    if dry_run:
        print("[DRY RUN] Single image mode")
        return True
    
    print("Creating single-image Short...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[-500:]}")
        return False
    
    print(f"✅ Single-image Short created: {output_file}")
    return True

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 create_video_dual.py <bg1> <bg2> <face> <audio> <output> [options]")
        print("\nArguments:")
        print("  bg1       First background image (0-12s)")
        print("  bg2       Second background image (12s-end)")
        print("  face      Face overlay video")
        print("  audio     Audio file")
        print("  output    Output video file")
        print("\nOptions:")
        print("  --switch N    Switch images at N seconds (default: 12)")
        print("  --dry-run     Show command without executing")
        print("  --single      Use only bg1 (fallback mode)")
        print("\nExample:")
        print("  python3 create_video_dual.py bg1.png bg2.png face.mp4 audio.mp3 output.mp4")
        sys.exit(1)
    
    bg1 = sys.argv[1]
    bg2 = sys.argv[2]
    face = sys.argv[3]
    audio = sys.argv[4]
    output = sys.argv[5]
    
    switch_time = 12
    dry_run = False
    single_mode = False
    
    # Parse optional args
    for i, arg in enumerate(sys.argv[6:], 6):
        if arg == '--switch' and i + 1 < len(sys.argv):
            switch_time = float(sys.argv[i + 1])
        elif arg == '--dry-run':
            dry_run = True
        elif arg == '--single':
            single_mode = True
    
    print("=" * 50)
    print("DUAL-IMAGE SHORT CREATOR")
    print("=" * 50)
    
    if single_mode:
        success = create_single_image_short(bg1, face, audio, output, dry_run=dry_run)
    else:
        success = create_dual_image_short(bg1, bg2, face, audio, output, 
                                          switch_time=switch_time, dry_run=dry_run)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
