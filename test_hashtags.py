#!/usr/bin/env python3
"""
Test hashtag generation for YouTube Shorts
"""

import sys
sys.path.insert(0, '/data/.openclaw/workspace')
from youtube_upload import generate_hashtags, generate_description

# Test titles
test_videos = [
    ("Why Your Phone Battery Dies (Planned Obsolescence)", "battery"),
    ("How Fiber Optic Cables Work (Light Speed Internet)", "fiber"),
    ("Why Your Power Cord Has That Third Prong", "ground_pin"),
    ("Why Airplane Windows Are Round", "airplane"),
    ("How Speakers Actually Make Sound", "speakers"),
]

print("🎯 YouTube Shorts Hashtag Generator Test")
print("=" * 70)

for title, topic in test_videos:
    print(f"\n📹 Video: {title}")
    print("-" * 70)
    
    description, tags = generate_description(title, hook="Did you know this? 🤯", topic=topic)
    
    print(f"📝 Description:\n{description}\n")
    print(f"🏷️  Tags ({len(tags)}): {', '.join(tags)}")
    print()

print("=" * 70)
print("\n✅ To use in upload:")
print("   python3 youtube_upload.py <auth_code> --title \"Your Title\" --topic battery")
