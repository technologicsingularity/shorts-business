#!/usr/bin/env python3
"""
Pre-generation validation script for YouTube Shorts.
Checks for duplicate topics and validates voice configuration.
"""

import json
import sys
import re
from pathlib import Path

def load_completed_videos():
    """Load completed videos tracker."""
    tracker_path = Path("/data/.openclaw/workspace/completed_videos.md")
    if not tracker_path.exists():
        return []
    
    content = tracker_path.read_text()
    # Extract topics from the "Topics to NEVER Duplicate" section
    never_duplicate = []
    in_never_section = False
    for line in content.split('\n'):
        if "Topics to NEVER Duplicate" in line:
            in_never_section = True
            continue
        if in_never_section and line.startswith("##"):
            break
        if in_never_section and line.startswith("- ❌"):
            topic = line.replace("- ❌", "").split("(")[0].strip().lower()
            never_duplicate.append(topic)
    return never_duplicate

def check_duplicate_topic(script_text):
    """Check if topic has already been covered."""
    completed = load_completed_videos()
    script_lower = script_text.lower()
    
    duplicates = []
    for topic in completed:
        # Check for significant word overlap
        topic_words = set(topic.split())
        script_words = set(script_lower.split())
        overlap = topic_words & script_words
        
        # If 60% or more of topic words appear in script, flag as duplicate
        if len(topic_words) > 0 and len(overlap) / len(topic_words) >= 0.6:
            duplicates.append(topic)
    
    return duplicates

def validate_voice_config():
    """Validate voice configuration - ensure we're not using Janet."""
    config_path = Path("/data/.openclaw/workspace/voice_config.json")
    
    if not config_path.exists():
        return False, "Voice config not found!"
    
    with open(config_path) as f:
        config = json.load(f)
    
    primary_voice = config.get("primary_voice", {})
    deprecated_voices = config.get("deprecated_voices", {})
    validation = config.get("validation", {})
    
    # Check primary voice is correct
    if primary_voice.get("name") != "TS_Soft_Innocent":
        return False, f"Wrong primary voice: {primary_voice.get('name')}"
    
    if primary_voice.get("id") != "IzvSBRjn2q72XdO9rbo8":
        return False, f"Wrong primary voice ID: {primary_voice.get('id')}"
    
    # Ensure blocked voices include all deprecated voices
    blocked = deprecated_voices.get("blocked", [])
    blocked_names = [v.get("name", "") for v in blocked]
    if "Janet" not in blocked_names:
        return False, "Janet not properly blocked in config!"
    if "Janet (alt)" not in blocked_names:
        return False, "Janet (alt) not properly blocked in config!"
    
    # Check validation rules are strict
    if not validation.get("abort_on_wrong_voice", False):
        return False, "Validation not strict enough - abort_on_wrong_voice must be true"
    
    blocked_ids = validation.get("blocked_ids", [])
    required_blocked = ["Pc1wcuuxmTb5FDmDgPjO", "eLDc7xhWxG2FElT3kUTj"]
    for blocked_id in required_blocked:
        if blocked_id not in blocked_ids:
            return False, f"Blocked voice ID {blocked_id} not in blocked_ids!"
    
    return True, f"✅ Voice config valid. Using: {primary_voice['name']}"

def main():
    """Main validation function."""
    print("=" * 60)
    print("PRE-GENERATION VALIDATION")
    print("=" * 60)
    
    # Check voice configuration
    print("\n🎙️  Checking voice configuration...")
    voice_valid, voice_msg = validate_voice_config()
    print(f"   {voice_msg}")
    
    if not voice_valid:
        print("\n❌ VOICE VALIDATION FAILED")
        print("   Fix voice_config.json before proceeding!")
        sys.exit(1)
    
    # Check for script file argument
    if len(sys.argv) < 2:
        print("\n⚠️  No script file provided for duplicate check")
        print("   Usage: python3 validate_before_create.py <script.txt>")
        sys.exit(0)
    
    script_path = Path(sys.argv[1])
    if not script_path.exists():
        print(f"\n❌ Script file not found: {script_path}")
        sys.exit(1)
    
    # Check for duplicate topics
    print("\n📋 Checking for duplicate topics...")
    script_text = script_path.read_text()
    duplicates = check_duplicate_topic(script_text)
    
    if duplicates:
        print(f"\n❌ DUPLICATE TOPIC DETECTED!")
        print(f"   This script matches previously completed topics:")
        for dup in duplicates:
            print(f"   - {dup}")
        print("\n   🚫 DO NOT PROCEED with video creation!")
        print("   Choose a different topic from completed_videos.md")
        sys.exit(1)
    
    print("   ✅ No duplicate topics found")
    
    print("\n" + "=" * 60)
    print("✅ ALL VALIDATIONS PASSED - SAFE TO PROCEED")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
