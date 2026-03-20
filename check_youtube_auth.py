#!/usr/bin/env python3
"""
Check and refresh YouTube credentials if needed
"""

import pickle
import json
from pathlib import Path

TOKEN_FILE = Path('/data/.openclaw/workspace/youtube_token.pickle')
CLIENT_SECRETS_FILE = Path('/data/.openclaw/workspace/client_secrets.json')

def check_credentials():
    print("🔐 Checking YouTube Credentials")
    print("=" * 60)
    
    if not TOKEN_FILE.exists():
        print("❌ No token file found")
        print("\nYou need to authenticate first:")
        print("  python3 youtube_upload.py")
        return False
    
    # Load token
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    print(f"Token type: {type(creds)}")
    
    if hasattr(creds, 'token'):
        print(f"✅ Valid Credentials object")
        print(f"   Token: {creds.token[:20]}...")
        print(f"   Has refresh token: {bool(creds.refresh_token)}")
        print(f"   Expired: {creds.expired}")
        return True
    elif isinstance(creds, dict):
        print(f"⚠️  Token is a dict - needs conversion")
        print(f"   Keys: {list(creds.keys())}")
        
        # Check if we have what we need
        if 'token' in creds and 'refresh_token' in creds:
            print("\n✅ Can convert to proper Credentials object")
            return True
        else:
            print("\n❌ Missing required fields")
            return False
    else:
        print(f"❌ Unknown token format: {type(creds)}")
        return False

if __name__ == '__main__':
    check_credentials()
