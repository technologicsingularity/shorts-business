#!/usr/bin/env python3
"""Upload keys video as YouTube Short - PUBLIC"""

import os
import pickle
import json
import warnings
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

warnings.filterwarnings('ignore')

TOKEN_FILE = '/data/.openclaw/workspace/youtube_token.pickle'
CLIENT_SECRETS_FILE = '/data/.openclaw/workspace/client_secrets.json'
VIDEO_FILE = '/data/.openclaw/workspace/keys_short_final.mp4'

def upload_short():
    # Load token dict
    with open(TOKEN_FILE, 'rb') as f:
        token_data = pickle.load(f)
    
    # Read client secrets
    with open(CLIENT_SECRETS_FILE) as f:
        client_config = json.load(f)['installed']
    
    # Create credentials
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=client_config['token_uri'],
        client_id=client_config['client_id'],
        client_secret=client_config['client_secret'],
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )
    
    # Refresh if needed
    if creds.expired:
        creds.refresh(Request())
        # Save refreshed token
        new_token = {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'expires_in': 3600,
            'token_type': 'Bearer',
            'scope': 'https://www.googleapis.com/auth/youtube.upload'
        }
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(new_token, f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': 'The Real Reason Keys Are Shaped That Way (You Won\'t Believe #3)',
            'description': '''🔑 Ever wondered why keys have those weird jagged shapes? 

It's not random—it's a tiny mechanical puzzle that predates computers by centuries. Every groove pushes a pin to the exact height needed to unlock the door.

#shorts #howitworks #locks #keys #engineering #mechanisms #didyouknow''',
            'tags': ['shorts', 'how it works', 'locks', 'keys', 'engineering', 'pin tumbler', 'master key', 'mechanisms', 'education'],
            'categoryId': '27'  # Education
        },
        'status': {
            'privacyStatus': 'public',  # PUBLIC for maximum reach
            'madeForKids': False
        }
    }
    
    print(f"Uploading {VIDEO_FILE}...")
    media = MediaFileUpload(VIDEO_FILE, mimetype='video/mp4', resumable=True)
    
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    
    print(f"\n✅ Upload complete!")
    print(f"Video ID: {response['id']}")
    print(f"URL: https://youtube.com/shorts/{response['id']}")
    return f"https://youtube.com/shorts/{response['id']}"

if __name__ == '__main__':
    url = upload_short()
