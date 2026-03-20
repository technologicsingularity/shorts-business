#!/usr/bin/env python3
"""
Check Gmail for new emails and report important ones
"""

import imaplib
import email
from email.header import decode_header
import os

def check_emails():
    # Connect to Gmail IMAP
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    
    # Login with App Password
    imap.login("technologicsingularity@gmail.com", "iuwd oadm bbjb bepi")
    
    # Select inbox
    imap.select("INBOX")
    
    # Search for unread emails
    status, messages = imap.search(None, 'UNSEEN')
    
    email_list = []
    
    if status == 'OK' and messages[0]:
        message_ids = messages[0].split()
        
        for msg_id in message_ids[-5:]:  # Last 5 unread
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
            
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = decode_header(msg["From"])[0][0]
                if isinstance(from_addr, bytes):
                    from_addr = from_addr.decode()
                
                email_list.append({
                    'subject': subject,
                    'from': from_addr,
                    'id': msg_id.decode()
                })
    
    imap.close()
    imap.logout()
    
    return email_list

if __name__ == '__main__':
    emails = check_emails()
    
    if emails:
        print("📧 NEW UNREAD EMAILS:")
        print("=" * 60)
        for e in emails:
            print(f"\nFrom: {e['from']}")
            print(f"Subject: {e['subject']}")
            print("-" * 60)
    else:
        print("📧 No new unread emails.")
