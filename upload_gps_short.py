#!/usr/bin/env python3
"""
Upload GPS Short to YouTube with existing token
"""

import os
import pickle
import warnings
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

warnings.filterwarnings('ignore')

TOKEN_FILE = '/data/.openclaw/workspace/youtube_token.pickle'
VIDEO_FILE = '/data/.openclaw/workspace/gps_short_final.mp4'

def upload_video():
    # Load credentials from pickle
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    print(f"Loaded credentials type: {type(creds)}")
    
    # Refresh if needed
    if hasattr(creds, 'expired') and creds.expired and hasattr(creds, 'refresh_token') and creds.refresh_token:
        print("Refreshing token...")
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
    
    # Build YouTube service
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Video metadata
    body = {
        'snippet': {
            'title': 'Your GPS Is Lying To You (How GPS Actually Works) #shorts',
            'description': '''Your GPS doesn't just "know" where you are. Here's the wild physics behind how it actually works — including Einstein's relativity! 🛰️

#shorts #gps #physics #science #einstein #relativity #space #satellites #howitworks #educational''',
            'tags': ['gps', 'how gps works', 'physics', 'einstein', 'relativity', 'satellites', 'space', 'science', 'educational', 'shorts'],
            'categoryId': '27'  # Education
        },
        'status': {
            'privacyStatus': 'public',  # PUBLIC
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Upload
    media = MediaFileUpload(VIDEO_FILE, mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    print(f"Uploading {VIDEO_FILE}...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    
    print(f"\n✅ Upload complete!")
    print(f"Video ID: {response['id']}")
    print(f"URL: https://youtube.com/shorts/{response['id']}")
    return response['id']

if __name__ == '__main__':
    video_id = upload_video()
    print(f"\nVideo URL: https://youtube.com/shorts/{video_id}")
