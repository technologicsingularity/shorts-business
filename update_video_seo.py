#!/usr/bin/env python3
"""
Update existing YouTube videos with SEO-optimized hashtags
Uses YouTube Data API to edit metadata without reuploading
"""

import os
import sys
import pickle
import json
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_FILE = '/data/.openclaw/workspace/youtube_token.pickle'
CLIENT_SECRETS_FILE = '/data/.openclaw/workspace/client_secrets.json'
SEO_CONFIG = Path('/data/.openclaw/workspace/youtube_seo_config.json')

def load_credentials():
    """Load saved YouTube credentials."""
    if not os.path.exists(TOKEN_FILE):
        print("❌ No saved credentials. Run youtube_upload.py first to authenticate.")
        return None
    
    with open(TOKEN_FILE, 'rb') as f:
        creds_data = pickle.load(f)
    
    from google.oauth2.credentials import Credentials
    
    # Handle different credential formats
    if isinstance(creds_data, dict):
        # Get client secrets for token refresh
        client_id = None
        client_secret = None
        if os.path.exists(CLIENT_SECRETS_FILE):
            with open(CLIENT_SECRETS_FILE) as f:
                client_config = json.load(f).get('installed', {})
                client_id = client_config.get('client_id')
                client_secret = client_config.get('client_secret')
        
        creds = Credentials(
            token=creds_data.get('access_token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/youtube']
        )
        
        # Save as proper Credentials object for future use
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
    else:
        creds = creds_data
    
    # Note: Token refresh may fail with invalid_scope if the original
    # token was granted with different scopes. For updates, we'll try
    # with the current token first.
    
    return creds

def load_seo_config():
    """Load SEO configuration."""
    if SEO_CONFIG.exists():
        with open(SEO_CONFIG) as f:
            return json.load(f)
    return {
        "default_tags": ["howitworks", "didyouknow", "edutok", "facts"],
        "topic_tags": {},
        "description_template": "{hook}\n\nFollow for more interesting facts!\n\n#Shorts #YouTubeShorts {hashtags}"
    }

def generate_hashtags(title, config):
    """Generate hashtags from title and config."""
    tags = list(config.get("default_tags", []))
    topic_tags = config.get("topic_tags", {})
    
    # Detect topic from title
    title_lower = title.lower()
    for topic_key, topic_tag_list in topic_tags.items():
        if topic_key in title_lower:
            tags.extend(topic_tag_list)
            break
    
    # Extract keywords from title
    keywords = [w for w in title_lower.replace('-', ' ').replace('_', ' ').split() 
                if len(w) > 3 and w not in ['this', 'that', 'with', 'from', 'your', 'that']]
    tags.extend(keywords[:3])
    
    # Remove duplicates
    seen = set()
    unique_tags = []
    for tag in tags:
        tag_clean = tag.lower().replace(' ', '')
        if tag_clean not in seen and len(tag) <= 500:  # YouTube tag length limit
            seen.add(tag_clean)
            unique_tags.append(tag)
    
    return unique_tags[:15]  # YouTube allows max 15 tags

def generate_description(title, tags, config):
    """Generate optimized description."""
    template = config.get("description_template", 
                          "{hook}\n\nFollow for more interesting facts!\n\n#Shorts #YouTubeShorts {hashtags}")
    
    hashtags = ' '.join([f'#{tag}' for tag in tags[:10]])
    hook = f"Did you know this? 🤯"
    
    return template.format(hook=hook, hashtags=hashtags)

def detect_topic(title):
    """Detect video topic from title."""
    title_lower = title.lower()
    topics = {
        "battery": ["battery", "phone battery", "dies"],
        "fiber": ["fiber", "optic", "cables", "internet"],
        "ground_pin": ["power cord", "third prong", "ground"],
        "airplane": ["airplane", "window", "plane"],
        "speakers": ["speakers", "sound", "audio"],
        "smoke_detector": ["smoke detector", "radioactive"],
        "camera": ["camera", "shutter"],
        "refrigerator": ["refrigerator", "fridge"],
        "microwave": ["microwave"],
        "keys": ["keys", "lock"],
        "gps": ["gps", "satellite"],
    }
    
    for topic, keywords in topics.items():
        if any(kw in title_lower for kw in keywords):
            return topic
    return None

def get_channel_videos(youtube, max_results=50):
    """Get videos from authenticated user's channel."""
    try:
        # First get the channel ID
        channels_response = youtube.channels().list(
            part='id,contentDetails',
            mine=True
        ).execute()
        
        if not channels_response['items']:
            print("❌ No channel found")
            return []
        
        channel_id = channels_response['items'][0]['id']
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from uploads playlist
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            playlist_response = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            ).execute()
            
            for item in playlist_response['items']:
                videos.append({
                    'id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet'].get('description', ''),
                    'published_at': item['snippet']['publishedAt']
                })
            
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break
        
        return videos
        
    except HttpError as e:
        print(f"❌ Error fetching videos: {e}")
        return []

def update_video_metadata(youtube, video_id, title, new_description, new_tags):
    """Update video metadata via API."""
    try:
        # First get current video to preserve other fields
        video_response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            print(f"❌ Video {video_id} not found")
            return False
        
        video = video_response['items'][0]
        snippet = video['snippet']
        
        # Update only what we want to change
        snippet['description'] = new_description
        snippet['tags'] = new_tags
        
        # Make the update
        update_response = youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()
        
        return True
        
    except HttpError as e:
        print(f"❌ Error updating video {video_id}: {e}")
        return False

def main():
    print("🎯 YouTube Video SEO Updater")
    print("=" * 60)
    
    # Load credentials
    creds = load_credentials()
    if not creds:
        sys.exit(1)
    
    # Load SEO config
    config = load_seo_config()
    
    # Build YouTube service
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Get videos
    print("\n📹 Fetching your videos...")
    videos = get_channel_videos(youtube, max_results=50)
    
    if not videos:
        print("❌ No videos found")
        sys.exit(1)
    
    print(f"✅ Found {len(videos)} videos")
    
    # Preview changes
    print("\n📋 Proposed Updates:")
    print("=" * 60)
    
    updates = []
    for video in videos:
        topic = detect_topic(video['title'])
        tags = generate_hashtags(video['title'], config)
        description = generate_description(video['title'], tags, config)
        
        has_tags = bool(video.get('description', '').count('#'))
        
        updates.append({
            'id': video['id'],
            'title': video['title'],
            'topic': topic,
            'tags': tags,
            'description': description,
            'url': f"https://youtube.com/shorts/{video['id']}",
            'has_existing_tags': has_tags
        })
        
        status = "✅ NEEDS UPDATE" if not has_tags else "⚠️  HAS TAGS (will overwrite)"
        print(f"\n{status}")
        print(f"Title: {video['title'][:60]}...")
        print(f"Topic: {topic or 'general'}")
        print(f"Tags: {', '.join(tags[:5])}...")
        print(f"URL: {updates[-1]['url']}")
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    print(f"\nThis will update {len(updates)} videos.")
    
    # Count how many need updates
    needs_update = sum(1 for u in updates if not u['has_existing_tags'])
    has_tags = sum(1 for u in updates if u['has_existing_tags'])
    
    print(f"  - {needs_update} videos need hashtags added")
    print(f"  - {has_tags} videos already have hashtags (will be overwritten)")
    
    response = input("\nProceed with updates? (yes/no/preview): ").lower().strip()
    
    if response == 'preview':
        print("\nFull descriptions preview:")
        for u in updates[:3]:  # Show first 3
            print(f"\n{u['title']}")
            print("-" * 40)
            print(u['description'])
        return
    
    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        sys.exit(0)
    
    # Apply updates
    print("\n🚀 Applying updates...")
    success_count = 0
    
    for update in updates:
        print(f"\nUpdating: {update['title'][:50]}...")
        
        if update_video_metadata(youtube, update['id'], update['title'], 
                                update['description'], update['tags']):
            print(f"  ✅ Updated - {update['url']}")
            success_count += 1
        else:
            print(f"  ❌ Failed")
    
    print("\n" + "=" * 60)
    print(f"✅ Updated {success_count}/{len(updates)} videos successfully")
    print("\nChanges may take a few minutes to appear on YouTube.")

if __name__ == '__main__':
    main()
