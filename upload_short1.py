#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'Why Cameras Make That Sound (Its 100% Fake)',
        'description': 'That satisfying camera click? Completely fake. Your smartphone has no mechanical shutter. Here is what is actually happening.\n\n#camera #smartphone #fake #howitworks #technology #digital #photography #hiddentech #shorts',
        'tags': ['camera', 'smartphone', 'fake', 'how it works', 'technology', 'digital', 'photography', 'shutter sound', 'shorts'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/camera_sound_short.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('Uploading Short #1: Why Cameras Make That Sound...')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n✅ Upload complete!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
print('Status: PUBLIC Short')
print('Note: Background needs regeneration when image service recovers')
