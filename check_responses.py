#!/usr/bin/env python3
"""
Check all emails (including read) for responses to our sent emails
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

def check_all_emails():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("technologicsingularity@gmail.com", "iuwd oadm bbjb bepi")
    imap.select("INBOX")
    
    # Search for emails in last 30 days (including read)
    since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
    status, messages = imap.search(None, f'SINCE {since_date}')
    
    results = []
    
    if status == 'OK' and messages[0]:
        message_ids = messages[0].split()
        
        for msg_id in message_ids:
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = decode_header(msg["From"])[0][0]
                if isinstance(from_addr, bytes):
                    from_addr = from_addr.decode()
                
                # Look for responses to our factory outreach
                if any(kw in subject.lower() for kw in ["re:", "fw:", "fwd:"]):
                    if any(domain in from_addr.lower() for domain in [
                        "hcsportswear.com", 
                        "goaluniform.com",
                        "factory",
                        "manufacturing"
                    ]):
                        results.append({
                            "from": from_addr,
                            "subject": subject,
                            "date": msg["Date"]
                        })
    
    imap.close()
    imap.logout()
    
    return results

if __name__ == '__main__':
    responses = check_all_emails()
    
    if responses:
        print("📨 POTENTIAL RESPONSES TO OUR EMAILS:")
        print("=" * 60)
        for r in responses:
            print(f"\nFrom: {r['from']}")
            print(f"Subject: {r['subject']}")
            print(f"Date: {r['date']}")
    else:
        print("📭 No responses found to our sent emails (last 30 days)")
        print("\n📤 Emails we sent:")
        print("  - admin@hcsportswear.com (3 emails)")
        print("  - contact@goaluniform.com (3 emails)")
        print("\n⚠️  These may have bounced or been ignored")
