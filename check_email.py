#!/usr/bin/env python3
"""Quick email check for technologicsingularity@gmail.com"""

import pickle
from googleapiclient.discovery import build

# Load existing YouTube token (same Google account)
with open('/data/.openclaw/workspace/youtube_token.pickle', 'rb') as f:
    creds = pickle.load(f)

# Build Gmail service
gmail = build('gmail', 'v1', credentials=creds)

# Get unread messages
results = gmail.users().messages().list(
    userId='me',
    q='is:unread in:inbox',
    maxResults=10
).execute()

messages = results.get('messages', [])

if not messages:
    print("📧 No unread emails in inbox.")
else:
    print(f"📧 {len(messages)} unread email(s):\n")
    
    for msg in messages[:5]:  # Show first 5
        email = gmail.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in email['payload']['headers']}
        subject = headers.get('Subject', 'No subject')
        sender = headers.get('From', 'Unknown')
        date = headers.get('Date', '')[:16]  # Trim date
        
        print(f"  📩 {subject}")
        print(f"     From: {sender}")
        print(f"     Date: {date}\n")

print("✅ Email check complete.")
