#!/usr/bin/env python3
import pickle
from googleapiclient.discovery import build

with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

youtube = build('youtube', 'v3', credentials=creds)

video_id = '6SRDDdN_9Xw'

# Update video to public with new title
body = {
    'id': video_id,
    'snippet': {
        'title': 'Tavern Shadows',
        'description': 'Cyberpunk ambient music with visual overlay.',
        'categoryId': '10'  # Music
    },
    'status': {
        'privacyStatus': 'public'
    }
}

response = youtube.videos().update(
    part='snippet,status',
    body=body
).execute()

print('✅ Video updated!')
print(f'Title: {response["snippet"]["title"]}')
print(f'Status: {response["status"]["privacyStatus"]}')
print(f'URL: https://youtube.com/watch?v={video_id}')
