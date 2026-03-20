#!/usr/bin/env python3
"""
Alita Model Router - Smart task-based model selection
Cheap by default, premium when needed. Avoids expensive Sonnet/Opus.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

ROUTER_CONFIG = Path("/data/.openclaw/workspace/model_router.json")

# Task classification patterns
TASK_PATTERNS = {
    "L1_MINIMAL": [
        r"\b(status|check|list|ls|count|verify|idle|simple|quick|basic)\b",
        r"\b(heartbeat|ping|health)\b",
        r"\bhow many\b",
        r"\bshow me\b(files?|directory|folder)",
    ],
    "L2_EFFICIENT": [
        r"\b(write|create|generate|make)\b.*\b(script|code|file|config)\b",
        r"\b(install|setup|configure)\b",
        r"\b(fetch|get|download)\b",
        r"\b(simple|basic)\b.*\b(script|code)\b",
    ],
    "L3_CAPABLE": [
        r"\b(video script|youtube shorts|content creation)\b",
        r"\b(analyze|research|summarize|review)\b",
        r"\b(edit|improve|rewrite|polish)\b",
        r"\b(explain|how does|why is)\b",
        r"\b(strategy|plan|approach)\b",
        r"\b(youtube|shorts|content)\b.*\b(script|video|create)\b",
    ],
    "L4_KIMI": [
        r"\b(debug|fix|error|bug|broken|issue)\b",
        r"\b(critical|important|urgent)\b",
        r"\b(architect|design|refactor|optimize)\b",
        r"\b(business|revenue|money|monetize)\b",
        r"\b(complex|difficult|hard)\b.*\b(debug|fix)\b",
    ],
}

TIER_MODELS = {
    "L1_MINIMAL": [
        "openrouter/free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "qwen/qwen3-coder:free",
    ],
    "L2_EFFICIENT": [
        "qwen/qwen3.5-flash-02-23",  # Best value, 1M context
        "qwen/qwen3.5-9b",           # Cheapest
        "mistralai/mistral-small-2603",
    ],
    "L3_CAPABLE": [
        "google/gemini-3.1-flash-lite-preview",  # Jordan's preferred
        "bytedance-seed/seed-2.0-lite",
        "z-ai/glm-5-turbo",
    ],
    "L4_KIMI": [
        "openrouter/moonshotai/kimi-k2.5",
    ],
}

COST_PER_1M = {
    # L1 - Free
    "openrouter/free": 0,
    "nvidia/nemotron-3-super-120b-a12b:free": 0,
    "qwen/qwen3-coder:free": 0,
    # L2 - Ultra cheap
    "qwen/qwen3.5-9b": 0.10,  # ~avg input/output
    "qwen/qwen3.5-flash-02-23": 0.16,
    "mistralai/mistral-small-2603": 0.38,
    # L3 - Mid tier
    "google/gemini-3.1-flash-lite-preview": 0.88,
    "bytedance-seed/seed-2.0-lite": 1.13,
    "z-ai/glm-5-turbo": 2.08,
    # L4 - Premium
    "openrouter/moonshotai/kimi-k2.5": 7.50,
}


def classify_task(message: str) -> str:
    """Classify task complexity based on message content."""
    message_lower = message.lower()
    
    # Check from highest to lowest priority
    for tier in ["L4_KIMI", "L3_CAPABLE", "L2_EFFICIENT", "L1_MINIMAL"]:
        for pattern in TASK_PATTERNS.get(tier, []):
            if re.search(pattern, message_lower):
                return tier
    
    # Default to L2 for unknown tasks (safe middle ground)
    return "L2_EFFICIENT"


def get_model_for_tier(tier: str, prefer_cheapest: bool = True) -> str:
    """Get best model for tier."""
    models = TIER_MODELS.get(tier, TIER_MODELS["L2_EFFICIENT"])
    
    if prefer_cheapest:
        # Return cheapest in tier
        return min(models, key=lambda m: COST_PER_1M.get(m, 999))
    else:
        # Return best quality (last in list)
        return models[-1]


def route_task(message: str, force_tier: Optional[str] = None) -> dict:
    """Route a task to appropriate model."""
    tier = force_tier or classify_task(message)
    model = get_model_for_tier(tier)
    cost = COST_PER_1M.get(model, 0)
    
    return {
        "tier": tier,
        "model": model,
        "estimated_cost_per_1m": f"${cost:.2f}",
        "reason": f"Task classified as {tier}",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: model_router.py '<task description>'")
        print("\nExamples:")
        print('  model_router.py "check disk space"')
        print('  model_router.py "write a python script to fetch data"')
        print('  model_router.py "create a youtube shorts script about batteries"')
        print('  model_router.py "debug this error in my code"')
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    result = route_task(task)
    
    print(f"\n🎯 Task: {task}")
    print(f"📊 Tier: {result['tier']}")
    print(f"🤖 Model: {result['model']}")
    print(f"💰 Cost: {result['estimated_cost_per_1m']} per 1M tokens")
    print(f"📝 Reason: {result['reason']}")
    
    # Show what would have been used for other tiers
    print("\n📋 Alternative Options:")
    for tier in ["L1_MINIMAL", "L2_EFFICIENT", "L3_CAPABLE", "L4_KIMI"]:
        if tier != result['tier']:
            alt_model = get_model_for_tier(tier)
            alt_cost = COST_PER_1M.get(alt_model, 0)
            print(f"   {tier}: {alt_model} (${alt_cost:.2f}/M)")


if __name__ == "__main__":
    main()
