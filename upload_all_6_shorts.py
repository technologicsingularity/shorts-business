#!/usr/bin/env python3
import os
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# OAuth credentials from environment
CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET', '')

# Load token data and reconstruct Credentials object
with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    token_data = pickle.load(f)

if isinstance(token_data, dict):
    scope = token_data.get('scope', 'https://www.googleapis.com/auth/youtube.upload')
    if isinstance(scope, str):
        scopes = [scope]
    else:
        scopes = scope
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=CLIENT_ID or token_data.get('client_id'),
        client_secret=CLIENT_SECRET or token_data.get('client_secret'),
        scopes=scopes
    )
else:
    creds = token_data

youtube = build('youtube', 'v3', credentials=creds)

videos = [
    {
        'file': '/data/.openclaw/workspace/shorts/2026-03-18/ground_pin_video.mp4',
        'title': 'Why Your Power Cord Has That Third Prong (It Saves Lives) #shorts',
        'desc': 'That third metal piece is not decoration. It is a lifeline.\n\n#electrical #safety #howitworks #electricity #grounding #engineering #power #shorts'
    },
    {
        'file': '/data/.openclaw/workspace/shorts/2026-03-18/round_windows_video.mp4',
        'title': 'Why Airplane Windows Are Round (Square Windows Kill) #shorts',
        'desc': 'The 1954 disaster that changed aviation forever.\n\n#airplane #aviation #engineering #safety #history #design #shorts'
    },
    {
        'file': '/data/.openclaw/workspace/shorts/2026-03-18/speakers_video.mp4',
        'title': 'How Speakers Actually Make Sound (Invisible Force) #shorts',
        'desc': 'Your music is just controlled air punches.\n\n#speakers #audio #music #physics #sound #technology #shorts'
    },
    {
        'file': '/data/.openclaw/workspace/shorts/2026-03-18/battery_video.mp4',
        'title': 'Why Your Phone Battery Dies (Planned Obsolescence) #shorts',
        'desc': 'Your battery is a consumable disguised as permanent.\n\n#battery #iphone #phone #technology #plannedobsolescence #charging #shorts'
    },
    {
        'file': '/data/.openclaw/workspace/shorts/2026-03-18/smoke_video.mp4',
        'title': 'Your Smoke Detector Is Radioactive (Nuclear Guardian) #shorts',
        'desc': 'There is a nuclear reactor on your ceiling.\n\n#smokedetector #radioactive #safety #nuclear #science #home #shorts'
    },
    {
        'file': '/data/.openclaw/workspace/shorts/2026-03-18/fiber_video.mp4',
        'title': 'How Fiber Optic Cables Work (Light Speed Internet) #shorts',
        'desc': 'The entire internet is just light trapped in glass.\n\n#fiberoptic #internet #technology #light #speed #cables #shorts'
    }
]

for i, video in enumerate(videos, 1):
    print(f'\n🎬 Uploading video {i}/6: {video["title"][:50]}...')
    
    body = {
        'snippet': {
            'title': video['title'],
            'description': video['desc'],
            'tags': ['shorts', 'how it works', 'technology', 'science'],
            'categoryId': '28'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    
    media = MediaFileUpload(video['file'], mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f'  Progress: {int(status.progress() * 100)}%')
    
    print(f'  ✅ Uploaded! ID: {response["id"]}')

print('\n🎉 All 6 videos uploaded successfully!')
