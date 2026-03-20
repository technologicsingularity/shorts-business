#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'Why Airplane Windows Have That Hole (It Saves Your Life)',
        'description': 'Every airplane window has a tiny hole at the bottom. It is not a defect. Here is why that little hole is literally holding the plane together.\n\n#airplane #aviation #physics #howitworks #technology #pressure #safety #hiddentech #shorts',
        'tags': ['airplane', 'aviation', 'physics', 'how it works', 'technology', 'pressure', 'safety', 'window', 'shorts'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/airplane_short.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('Uploading Short #3: Why Airplane Windows Have That Hole...')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n✅ Upload complete!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
print('Status: PUBLIC Short')
print('DAILY GOAL: 3 of 3 Shorts complete! 🎉')
