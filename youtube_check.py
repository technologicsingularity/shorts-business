#!/usr/bin/env python3
"""
Fetch YouTube video details using our authenticated API
"""

import pickle
from googleapiclient.discovery import build

TOKEN_FILE = '/data/.openclaw/workspace/youtube_token.pickle'

def get_youtube_service():
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    return build('youtube', 'v3', credentials=creds)

def get_video_details(video_id):
    youtube = get_youtube_service()
    
    response = youtube.videos().list(
        part='snippet,statistics,contentDetails',
        id=video_id
    ).execute()
    
    if response['items']:
        video = response['items'][0]
        snippet = video['snippet']
        stats = video['statistics']
        
        print(f"Title: {snippet['title']}")
        print(f"Description: {snippet['description'][:200]}...")
        print(f"Published: {snippet['publishedAt']}")
        print(f"Views: {stats.get('viewCount', 0)}")
        print(f"Likes: {stats.get('likeCount', 0)}")
        print(f"Comments: {stats.get('commentCount', 0)}")
        print(f"Tags: {snippet.get('tags', [])}")
        return video
    else:
        print("Video not found")
        return None

def list_channel_videos(max_results=10):
    youtube = get_youtube_service()
    
    # Get channel ID
    channels_response = youtube.channels().list(
        part='id',
        mine=True
    ).execute()
    
    if not channels_response['items']:
        print("No channel found")
        return
    
    channel_id = channels_response['items'][0]['id']
    
    # Get uploads playlist
    playlist_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get videos from uploads playlist
    videos_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=max_results
    ).execute()
    
    print(f"\n=== Recent Videos ===\n")
    for item in videos_response['items']:
        snippet = item['snippet']
        print(f"Title: {snippet['title']}")
        print(f"Video ID: {snippet['resourceId']['videoId']}")
        print(f"Published: {snippet['publishedAt']}")
        print(f"URL: https://youtube.com/watch?v={snippet['resourceId']['videoId']}")
        print("-" * 50)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        get_video_details(video_id)
    else:
        list_channel_videos()
