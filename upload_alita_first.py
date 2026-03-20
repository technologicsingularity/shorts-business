#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': 'Why The Sky Isnt Purple (Your Eyes Are Lying To You)',
        'description': 'Violet light scatters MORE than blue. So why is not the sky purple? The answer is in your eyes.\n\n#sky #physics #howitworks #colors #light #vision #ultraviolet #science #shorts',
        'tags': ['sky', 'physics', 'how it works', 'colors', 'light', 'vision', 'ultraviolet', 'science', 'shorts'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/alita_first_short.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('🎙️ Uploading FIRST Alita-voiced Short...')
print('This is history in the making!')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n🎉 UPLOAD COMPLETE!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/watch?v={response["id"]}')
print('✨ First video with Alita\'s cloned voice is LIVE!')
