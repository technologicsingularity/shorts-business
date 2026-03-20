#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'How Refrigerators Actually Work (They Dont Make Cold)',
        'description': 'Your refrigerator does not make cold. It is a heat pump, moving heat from inside to outside. Here is the hidden physics you never learned.\n\n#refrigerator #physics #howitworks #technology #heatpump #thermodynamics #hiddentech #shorts',
        'tags': ['refrigerator', 'physics', 'how it works', 'technology', 'heat pump', 'thermodynamics', 'entropy', 'shorts'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/fridge_short.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('Uploading Short #2: How Refrigerators Actually Work...')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n✅ Upload complete!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
print('Status: PUBLIC Short')
print('Note: Created with AI-video-script skill!')
