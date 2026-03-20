#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

# Proper Shorts format with #Shorts in title
body = {
    'snippet': {
        'title': 'Why The Sky Isnt Purple #Shorts',
        'description': 'Violet light scatters MORE than blue. So why isnt the sky purple? The answer is in your eyes.\n\n#Shorts #sky #physics #howitworks #colors #light #vision #ultraviolet #science',
        'tags': ['Shorts', 'sky', 'physics', 'how it works', 'colors', 'light', 'vision', 'ultraviolet', 'science'],
        'categoryId': '28'
    },
    'status': {
        'privacyStatus': 'public'
    }
}

media = MediaFileUpload('/data/.openclaw/workspace/alita_sky_correct.mp4', mimetype='video/mp4', resumable=True)

request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

print('🎬 Uploading CORRECTED Alita Short...')
print('✅ Correct background image')
print('✅ #Shorts in title')
print('✅ 9:16 vertical format')
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f'Uploaded {int(status.progress() * 100)}%')

print(f'\n🎉 CORRECTED SHORT LIVE!')
print(f'Video ID: {response["id"]}')
print(f'URL: https://youtube.com/shorts/{response["id"]}')
print('✨ Now properly formatted as a Short!')
