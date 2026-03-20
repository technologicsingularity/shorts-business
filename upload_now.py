#!/usr/bin/env python3
"""
Upload video using saved token
"""
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'How Smoke Detectors Actually Work (Theres Nuclear Material On Your Ceiling)',
        'description': 'Your smoke detector contains Americium-241, a radioactive element. Here is how it uses nuclear decay to save your life.\n\n#smokedetector #radioactive #nuclear #howitworks #technology #americium #physics #hiddentech',
        'tags': ['smoke detector', 'americium-241', 'radioactive', 'nuclear', 'how it works', 'technology', 'physics', 'ionization', 'hidden tech'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'private'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/smoke_detector_video.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('Uploading smoke detector video...')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n✅ Upload complete!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
