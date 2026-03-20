#!/usr/bin/env python3
"""
Fix YouTube token scope issue
"""

import pickle
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google.auth.exceptions

TOKEN_FILE = Path('/data/.openclaw/workspace/youtube_token.pickle')
CLIENT_SECRETS_FILE = Path('/data/.openclaw/workspace/client_secrets.json')

def fix_token():
    print("🔧 Fixing YouTube Token")
    print("=" * 60)
    
    # Load existing token data
    with open(TOKEN_FILE, 'rb') as f:
        data = pickle.load(f)
    
    print(f"Original token type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Token keys: {list(data.keys())}")
        print(f"Scope: {data.get('scope', 'N/A')}")
        
        # Load client secrets
        with open(CLIENT_SECRETS_FILE) as f:
            client_config = json.load(f)['installed']
        
        # Create credentials with the scope the token was originally granted
        original_scope = data.get('scope', '')
        
        # Use the actual scope from the token
        creds = Credentials(
            token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_config['client_id'],
            client_secret=client_config['client_secret'],
            scopes=original_scope.split() if original_scope else ['https://www.googleapis.com/auth/youtube']
        )
        
        print(f"\n✅ Created Credentials object")
        print(f"   Scopes: {creds.scopes}")
        
        # Try to refresh
        try:
            creds.refresh(Request())
            print("   Token refreshed successfully!")
            
            # Save fixed credentials
            with open(TOKEN_FILE, 'wb') as f:
                pickle.dump(creds, f)
            
            print("\n✅ Token fixed and saved!")
            return True
            
        except google.auth.exceptions.RefreshError as e:
            print(f"\n❌ Cannot refresh: {e}")
            print("\nYou need to re-authenticate:")
            print("  python3 youtube_upload.py")
            return False
    
    return True

if __name__ == '__main__':
    fix_token()
