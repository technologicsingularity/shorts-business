#!/usr/bin/env python3
"""
YouTube Video Uploader - Final working version
"""

import os
import sys
import pickle
import base64
import hashlib
import secrets
import warnings
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

warnings.filterwarnings('ignore')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = '/data/.openclaw/workspace/client_secrets.json'
TOKEN_FILE = '/data/.openclaw/workspace/youtube_token.pickle'
PKCE_FILE = '/data/.openclaw/workspace/youtube_pkce.pickle'

def generate_pkce():
    """Generate PKCE verifier and challenge."""
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).rstrip(b'=').decode('ascii')
    
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('ascii')).digest()
    ).rstrip(b'=').decode('ascii')
    
    return code_verifier, code_challenge

def save_pkce(verifier):
    with open(PKCE_FILE, 'wb') as f:
        pickle.dump(verifier, f)

def load_pkce():
    if os.path.exists(PKCE_FILE):
        with open(PKCE_FILE, 'rb') as f:
            return pickle.load(f)
    return None

def generate_hashtags(video_title, topic=None):
    """Generate relevant hashtags for video based on title and topic."""
    seo_config_path = Path('/data/.openclaw/workspace/youtube_seo_config.json')
    
    # Load SEO config
    if seo_config_path.exists():
        with open(seo_config_path) as f:
            config = json.load(f)
    else:
        # Default hashtags if config missing
        config = {
            "default_tags": ["howitworks", "didyouknow", "edutok", "facts"],
            "topic_tags": {}
        }
    
    # Start with default tags
    tags = list(config.get("default_tags", []))
    
    # Try to detect topic from title if not provided
    if not topic:
        title_lower = video_title.lower()
        for topic_key, topic_tags in config.get("topic_tags", {}).items():
            if topic_key in title_lower:
                topic = topic_key
                break
    
    # Add topic-specific tags
    if topic and topic in config.get("topic_tags", {}):
        tags.extend(config["topic_tags"][topic])
    
    # Extract keywords from title (simple approach)
    title_words = video_title.lower().replace('-', ' ').replace('_', ' ').split()
    keywords = [w for w in title_words if len(w) > 3 and w not in ['this', 'that', 'with', 'from', 'your']]
    tags.extend(keywords[:3])  # Add up to 3 keywords from title
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        tag_clean = tag.lower().replace(' ', '')
        if tag_clean not in seen:
            seen.add(tag_clean)
            unique_tags.append(tag)
    
    # Limit to max tags
    max_tags = config.get("max_tags", 15)
    return unique_tags[:max_tags]

def generate_description(video_title, hook=None, topic=None):
    """Generate optimized description with hashtags."""
    seo_config_path = Path('/data/.openclaw/workspace/youtube_seo_config.json')
    
    if seo_config_path.exists():
        with open(seo_config_path) as f:
            config = json.load(f)
    else:
        config = {"description_template": "{hook}\n\n#Shorts #YouTubeShorts {hashtags}"}
    
    # Generate hashtags
    tags = generate_hashtags(video_title, topic)
    hashtags = ' '.join([f'#{tag}' for tag in tags[:8]])  # Use top 8 as hashtags
    
    # Default hook if not provided
    if not hook:
        hook = "Did you know this? 🤯"
    
    # Format description
    template = config.get("description_template", "{hook}\n\n#Shorts #YouTubeShorts {hashtags}")
    description = template.format(hook=hook, hashtags=hashtags)
    
    return description, tags

def get_auth_url():
    """Generate authorization URL with PKCE."""
    code_verifier, code_challenge = generate_pkce()
    save_pkce(code_verifier)
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES,
        redirect_uri='http://localhost:8080'
    )
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        code_challenge=code_challenge,
        code_challenge_method='S256'
    )
    return auth_url

def upload_with_auth_code(auth_code, video_file, title, description='', tags=None, privacy_status='private'):
    """Upload using provided auth code."""
    code_verifier = load_pkce()
    if not code_verifier:
        print("ERROR: No PKCE verifier found. Please generate a new auth URL.")
        return None
    
    # Use requests_oauthlib directly for more control
    from requests_oauthlib import OAuth2Session
    import json
    
    # Read client secrets
    with open(CLIENT_SECRETS_FILE) as f:
        client_config = json.load(f)['installed']
    
    client_id = client_config['client_id']
    client_secret = client_config['client_secret']
    token_uri = client_config['token_uri']
    
    # Accept the broader scope Google returns
    effective_scope = ['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.upload']
    
    oauth = OAuth2Session(
        client_id,
        redirect_uri='http://localhost:8080',
        scope=effective_scope
    )
    
    try:
        token = oauth.fetch_token(
            token_uri,
            code=auth_code,
            code_verifier=code_verifier,
            client_secret=client_secret
        )
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None
    
    # Convert to google credentials
    from google.oauth2.credentials import Credentials
    
    creds = Credentials(
        token=token['access_token'],
        refresh_token=token.get('refresh_token'),
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=effective_scope
    )
    
    # Save token for future use
    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)
    
    # Clean up PKCE file
    if os.path.exists(PKCE_FILE):
        os.remove(PKCE_FILE)
    
    # Now upload
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }
    
    media = MediaFileUpload(video_file, mimetype='video/mp4', resumable=True)
    
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    
    print(f"Uploading {video_file}...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    
    print(f"\n✅ Upload complete!")
    print(f"Video ID: {response['id']}")
    print(f"URL: https://youtube.com/watch?v={response['id']}")
    return response['id']

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload video to YouTube')
    parser.add_argument('auth_code', nargs='?', help='Authorization code')
    parser.add_argument('--video', '-v', default='/data/.openclaw/workspace/output_video_looped.mp4', help='Video file path')
    parser.add_argument('--title', '-t', default='Alita - Cyberpunk Test', help='Video title')
    parser.add_argument('--description', '-d', help='Video description (auto-generated if not provided)')
    parser.add_argument('--topic', help='Video topic for hashtag generation (e.g., battery, airplane, gps)')
    parser.add_argument('--hook', help='Description hook text')
    parser.add_argument('--tags', nargs='+', help='Additional tags')
    parser.add_argument('--status', default='private', choices=['private', 'unlisted', 'public'], help='Privacy status')
    
    args = parser.parse_args()
    
    if not args.auth_code:
        # Just show auth URL
        auth_url = get_auth_url()
        print("\n" + "="*60)
        print("YouTube Authorization Required")
        print("="*60)
        print(f"\n1. Visit this URL in your browser:\n")
        print(auth_url)
        print("\n2. Sign in and authorize the app")
        print("3. You'll be redirected to localhost (will show error - that's OK)")
        print("4. Copy the CODE from the URL (after 'code=')")
        print("5. Run: python3 youtube_upload.py <auth_code> [options]")
        print("\nOptions:")
        print("  --video, -v     Video file path")
        print("  --title, -t     Video title")
        print("  --topic         Topic for auto-hashtags (battery, airplane, gps, etc.)")
        print("  --status        Privacy: private/unlisted/public")
        print("\n" + "="*60)
        sys.exit(0)
    
    # Auto-generate description and hashtags if not provided
    if not args.description:
        description, tags = generate_description(args.title, args.hook, args.topic)
        print(f"\n📝 Auto-generated description:")
        print(f"{description}")
        print(f"\n🏷️  Tags: {', '.join(tags)}")
    else:
        description = args.description
        tags = generate_hashtags(args.title, args.topic)
    
    # Merge additional tags if provided
    if args.tags:
        tags = list(set(tags + args.tags))
    
    try:
        video_id = upload_with_auth_code(
            args.auth_code, 
            args.video, 
            args.title, 
            description, 
            tags,
            args.status
        )
        
        if video_id:
            print(f"\n🔗 Video URL: https://youtube.com/shorts/{video_id}")
            print(f"📊 Tags used: {', '.join(tags[:15])}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
