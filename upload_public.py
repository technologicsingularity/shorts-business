#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'Why Your Phone Gets Hot (The Secret Battery Battle Inside)',
        'description': 'Your smartphone is fighting a secret battle every time you use it. Inside your battery, lithium ions create electrical friction that escapes as heat. Fast charging makes it worse. Here is what is actually happening.\n\n#smartphone #battery #physics #howitworks #technology #charging #lithium #hiddentech',
        'tags': ['smartphone', 'battery', 'physics', 'how it works', 'technology', 'charging', 'lithium', 'heat', 'internal resistance', 'fast charging'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'  # CHANGED TO PUBLIC
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/phone_heat_video.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('Uploading phone heat video (PUBLIC)...')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n✅ Upload complete!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
print('Status: PUBLIC 🌐')
