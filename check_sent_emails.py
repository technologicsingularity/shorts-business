#!/usr/bin/env python3
"""
Check sent emails to identify bounces and track what we sent
"""

import imaplib
import email
from email.header import decode_header
import json
from pathlib import Path
from datetime import datetime, timedelta

TRACKING_DIR = Path("/data/.openclaw/workspace/email_tracking")
SENT_TRACKING_FILE = TRACKING_DIR / "sent_emails.json"

def load_json(f):
    try:
        return json.loads(f.read_text())
    except:
        return []

def save_json(f, data):
    f.write_text(json.dumps(data, indent=2))

def check_sent():
    """Check recently sent emails"""
    TRACKING_DIR.mkdir(exist_ok=True)
    sent_history = load_json(SENT_TRACKING_FILE)
    
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("technologicsingularity@gmail.com", "iuwd oadm bbjb bepi")
    imap.select('"[Gmail]/Sent Mail"')
    
    # Search for emails sent in last 30 days
    since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
    status, messages = imap.search(None, f'SINCE {since_date}')
    
    sent_emails = []
    
    if status == 'OK' and messages[0]:
        message_ids = messages[0].split()[-20:]  # Last 20 sent
        
        for msg_id in message_ids:
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                to_addr = decode_header(msg["To"])[0][0]
                if isinstance(to_addr, bytes):
                    to_addr = to_addr.decode()
                
                date = msg["Date"]
                
                sent_emails.append({
                    "to": to_addr,
                    "subject": subject,
                    "date": date,
                    "msg_id": msg_id.decode()
                })
    
    imap.close()
    imap.logout()
    
    # Update tracking
    save_json(SENT_TRACKING_FILE, sent_emails)
    
    return sent_emails

if __name__ == '__main__':
    emails = check_sent()
    print(f"📤 Last {len(emails)} sent emails:")
    print("=" * 60)
    for e in emails:
        print(f"\nTo: {e['to']}")
        print(f"Subject: {e['subject']}")
        print(f"Date: {e['date']}")
