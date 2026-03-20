#!/usr/bin/env python3
"""Quick upload using existing token."""

import pickle
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_FILE = '/data/.openclaw/workspace/youtube_token.pickle'

def upload_video(video_file, title, description, tags, privacy='public'):
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'
        },
        'status': {'privacyStatus': privacy}
    }
    
    media = MediaFileUpload(video_file, mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    print(f"Uploading {title}...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    
    return response['id']

if __name__ == '__main__':
    import sys
    import json
    from pathlib import Path
    
    # Load SEO config for hashtags
    seo_config = json.load(open('/data/.openclaw/workspace/youtube_seo_config.json'))
    
    # Video configs
    videos = [
        ('/data/.openclaw/workspace/shorts/2026-03-18/smoke_video_new.mp4', 
         'Your Smoke Detector Is Radioactive (Nuclear Guardian)', 'smoke_detector'),
        ('/data/.openclaw/workspace/shorts/2026-03-18/battery_video_new.mp4',
         'Why Your Phone Battery Dies (Planned Obsolescence)', 'battery'),
        ('/data/.openclaw/workspace/shorts/2026-03-18/speakers_video_new.mp4',
         'How Speakers Actually Make Sound (Invisible Force)', 'speakers'),
        ('/data/.openclaw/workspace/shorts/2026-03-18/fiber_video_new.mp4',
         'How Fiber Optic Cables Work (Light Speed Internet)', 'fiber'),
        ('/data/.openclaw/workspace/shorts/2026-03-18/ground_pin_video_new.mp4',
         'Why Your Power Cord Has That Third Prong (It Saves Lives)', 'ground_pin'),
        ('/data/.openclaw/workspace/shorts/2026-03-18/round_windows_video_new.mp4',
         'Why Airplane Windows Are Round (Square Windows Kill)', 'airplane'),
    ]
    
    results = []
    for video_file, title, topic in videos:
        if not os.path.exists(video_file):
            print(f"SKIP: {video_file} not found")
            continue
            
        # Generate tags and description
        tags = list(seo_config['default_tags'])
        if topic in seo_config['topic_tags']:
            tags.extend(seo_config['topic_tags'][topic])
        
        hook = "Did you know this? 🤯"
        hashtags = ' '.join([f'#{t}' for t in tags[:8]])
        description = f"{hook}\n\nFollow for more interesting facts!\n\n#Shorts #YouTubeShorts {hashtags}"
        
        try:
            video_id = upload_video(video_file, title, description, tags[:15])
            print(f"✅ Uploaded: https://youtube.com/shorts/{video_id}\n")
            results.append((title, video_id))
        except Exception as e:
            print(f"❌ Error uploading {title}: {e}\n")
            results.append((title, f"ERROR: {e}"))
    
    print("\n" + "="*60)
    print("UPLOAD SUMMARY")
    print("="*60)
    for title, result in results:
        print(f"{title}")
        print(f"  → {result}\n")
