#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

description_text = """Your microwave is not heating your food. It is doing something far stranger. Here is the hidden mechanism behind how microwave ovens actually work.

#microwave #howitworks #science #physics #technology #electromagnetic #wifi #hiddentech #shorts"""

body = {
    'snippet': {
        'title': 'How Microwave Ovens Actually Work (They Dont Heat Your Food)',
        'description': description_text,
        'tags': ['microwave', 'how it works', 'science', 'physics', 'technology', 'electromagnetic', 'wifi', 'water molecules', 'hidden tech', 'shorts'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/microwave_short_fixed.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('Uploading FIXED Short: How Microwave Ovens Actually Work...')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n✅ Upload complete!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
print('Status: PUBLIC Short')