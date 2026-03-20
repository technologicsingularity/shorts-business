#!/usr/bin/env python3
"""
Apply Alita's Model Router configuration to OpenClaw
Sets up tier-based defaults with proper fallbacks
"""

import json
import subprocess
from pathlib import Path

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

def apply_router_config():
    """Apply model router config to OpenClaw."""
    
    config = {
        "agents": {
            "defaults": {
                "model": {
                    "primary": "openrouter/qwen/qwen3.5-flash-02-23",
                    "fallbacks": [
                        "openrouter/free",
                        "google/gemini-3.1-flash-lite-preview",
                        "openrouter/moonshotai/kimi-k2.5",
                        "qwen/qwen3-coder:free",
                        "nvidia/nemotron-3-super-120b-a12b:free"
                    ]
                }
            }
        }
    }
    
    print("🎯 Applying Alita's Model Router Config")
    print("=" * 50)
    print("\n📊 Tier System:")
    print("  L1 (Free):     openrouter/free, nemotron:free")
    print("  L2 (Cheap):    qwen3.5-flash ($0.16/M), qwen3.5-9b ($0.10/M)")
    print("  L3 (Mid):      gemini-3.1-flash-lite ($0.88/M) ⭐ Jordan's pick")
    print("  L4 (Premium):  kimi-k2.5 ($7.50/M) - Debug/critical only")
    print("\n🚫 Blocked: Sonnet, Opus 4.6, GPT-5.4 (too expensive)")
    print("=" * 50)
    
    # Check current config
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            current = json.load(f)
        old_model = current.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "unknown")
        print(f"\n🔄 Current primary: {old_model}")
        print(f"✅ New primary: {config['agents']['defaults']['model']['primary']}")
    
    print("\n📋 To apply changes, run:")
    print("  openclaw gateway restart")
    print("\n💡 To route a specific task, run:")
    print("  python3 /data/.openclaw/workspace/model_router.py '<your task>'")
    
    return config

if __name__ == "__main__":
    apply_router_config()
