#!/usr/bin/env python3
"""
Read specific email content
"""

import imaplib
import email
from email.header import decode_header

def read_email_by_subject(search_subject):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("technologicsingularity@gmail.com", "iuwd oadm bbjb bepi")
    imap.select("INBOX")
    
    # Search for the email
    status, messages = imap.search(None, f'SUBJECT "{search_subject}"')
    
    if status == 'OK' and messages[0]:
        msg_id = messages[0].split()[-1]  # Get the most recent matching
        
        status, msg_data = imap.fetch(msg_id, '(RFC822)')
        if status == 'OK':
            msg = email.message_from_bytes(msg_data[0][1])
            
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            from_addr = decode_header(msg["From"])[0][0]
            if isinstance(from_addr, bytes):
                from_addr = from_addr.decode()
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                except:
                    pass
            
            print(f"From: {from_addr}")
            print(f"Subject: {subject}")
            print(f"Date: {msg['Date']}")
            print("\n" + "="*60)
            print("BODY:")
            print("="*60)
            print(body)
    
    imap.close()
    imap.logout()

if __name__ == '__main__':
    read_email_by_subject("RE: Athletic Shorts Manufacturing Inquiry")
