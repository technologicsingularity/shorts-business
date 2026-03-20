#!/usr/bin/env python3
"""
Smart Gmail checker - reads content, takes action, tracks state
"""

import imaplib
import email
from email.header import decode_header
import json
from pathlib import Path
from datetime import datetime

# Tracking files
TRACKING_DIR = Path("/data/.openclaw/workspace/email_tracking")
DEAD_EMAILS_FILE = TRACKING_DIR / "dead_emails.json"
PENDING_FILE = TRACKING_DIR / "pending_responses.json"
RECEIVED_FILE = TRACKING_DIR / "received_responses.json"
FACTORIES_FILE = TRACKING_DIR / "factories.json"

def ensure_tracking():
    TRACKING_DIR.mkdir(exist_ok=True)
    for f in [DEAD_EMAILS_FILE, PENDING_FILE, RECEIVED_FILE, FACTORIES_FILE]:
        if not f.exists():
            f.write_text("[]")

def load_json(f):
    try:
        return json.loads(f.read_text())
    except:
        return []

def save_json(f, data):
    f.write_text(json.dumps(data, indent=2))

def extract_body(msg):
    """Extract email body text"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
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
    return body[:2000]  # First 2000 chars

def is_bounce(subject, body, from_addr):
    """Detect bounced emails"""
    bounce_keywords = [
        "delivery status notification", "undelivered", "returned to sender",
        "bounce", "failure notice", "delivery failed", "could not be delivered",
        "550", "551", "552", "553", "554", "recipient rejected"
    ]
    text = (subject + " " + body + " " + from_addr).lower()
    return any(kw in text for kw in bounce_keywords)

def extract_bounced_email(body):
    """Try to extract the bounced email address from bounce message"""
    import re
    # Look for email patterns in bounce message
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', body)
    # Filter out common non-bounced addresses
    filtered = [e for e in emails if 'mailer-daemon' not in e and 'postmaster' not in e]
    return filtered[0] if filtered else None

def categorize_email(subject, body, from_addr):
    """Categorize email type"""
    text = (subject + " " + body + " " + from_addr).lower()
    
    if is_bounce(subject, body, from_addr):
        return "bounce"
    
    if any(kw in text for kw in ["factory", "manufacturer", "supplier", "moq", "quote", "pricing", "sample"]):
        return "factory_response"
    
    if "re:" in subject.lower() or "fwd:" in subject.lower():
        return "reply"
    
    if any(kw in text for kw in ["youtube", "video", "copyright", "claim"]):
        return "youtube"
    
    return "other"

def check_emails():
    ensure_tracking()
    
    dead_emails = load_json(DEAD_EMAILS_FILE)
    pending = load_json(PENDING_FILE)
    received = load_json(RECEIVED_FILE)
    
    # Connect to Gmail
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("technologicsingularity@gmail.com", "iuwd oadm bbjb bepi")
    imap.select("INBOX")
    
    # Search for unread
    status, messages = imap.search(None, 'UNSEEN')
    
    results = {
        "bounces": [],
        "factory_responses": [],
        "replies": [],
        "other": [],
        "total": 0
    }
    
    if status == 'OK' and messages[0]:
        message_ids = messages[0].split()
        results["total"] = len(message_ids)
        
        for msg_id in message_ids:
            status, msg_data = imap.fetch(msg_id, '(RFC822)')
            
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Decode headers
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = decode_header(msg["From"])[0][0]
                if isinstance(from_addr, bytes):
                    from_addr = from_addr.decode()
                
                body = extract_body(msg)
                category = categorize_email(subject, body, from_addr)
                
                email_data = {
                    "id": msg_id.decode(),
                    "subject": subject,
                    "from": from_addr,
                    "body_preview": body[:500],
                    "date": datetime.now().isoformat(),
                    "category": category
                }
                
                if category == "bounce":
                    bounced_email = extract_bounced_email(body)
                    if bounced_email and bounced_email not in [d["email"] for d in dead_emails]:
                        dead_emails.append({
                            "email": bounced_email,
                            "reason": "Bounce/Undeliverable",
                            "date": datetime.now().isoformat(),
                            "subject": subject
                        })
                        results["bounces"].append(email_data)
                
                elif category == "factory_response":
                    results["factory_responses"].append(email_data)
                    # Add to received responses
                    received.append(email_data)
                
                elif category == "reply":
                    results["replies"].append(email_data)
                    received.append(email_data)
                
                else:
                    results["other"].append(email_data)
    
    imap.close()
    imap.logout()
    
    # Save tracking data
    save_json(DEAD_EMAILS_FILE, dead_emails)
    save_json(RECEIVED_FILE, received)
    
    return results

def generate_report(results):
    """Generate human-readable report"""
    lines = []
    lines.append("📧 GMAIL CHECK REPORT")
    lines.append("=" * 60)
    lines.append(f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"New emails: {results['total']}")
    lines.append("")
    
    if results["bounces"]:
        lines.append("🚫 BOUNCED EMAILS (Added to dead list):")
        for b in results["bounces"]:
            lines.append(f"  - {b['from']}")
            lines.append(f"    Subject: {b['subject']}")
        lines.append("")
    
    if results["factory_responses"]:
        lines.append("🏭 FACTORY RESPONSES:")
        for f in results["factory_responses"]:
            lines.append(f"  From: {f['from']}")
            lines.append(f"  Subject: {f['subject']}")
            lines.append(f"  Preview: {f['body_preview'][:200]}...")
            lines.append("  ACTION NEEDED: Extract pricing/MOQ, update factory tracker")
            lines.append("")
    
    if results["replies"]:
        lines.append("↩️  REPLIES TO OUR EMAILS:")
        for r in results["replies"]:
            lines.append(f"  From: {r['from']}")
            lines.append(f"  Subject: {r['subject']}")
            lines.append(f"  Preview: {r['body_preview'][:200]}...")
            lines.append("  ACTION NEEDED: Determine if reply required")
            lines.append("")
    
    if not any([results["bounces"], results["factory_responses"], results["replies"]]):
        if results["other"]:
            lines.append(f"📨 {len(results['other'])} other emails (no action needed)")
        else:
            lines.append("✅ No new actionable emails.")
    
    # Show dead list count
    dead = load_json(DEAD_EMAILS_FILE)
    if dead:
        lines.append(f"\n🚫 Dead email list: {len(dead)} addresses blocked")
    
    return "\n".join(lines)

if __name__ == '__main__':
    results = check_emails()
    print(generate_report(results))
