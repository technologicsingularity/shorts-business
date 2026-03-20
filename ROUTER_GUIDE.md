# 🎯 Alita's Smart Model Router

**Your automated, cost-conscious AI model selection system.**

No more thinking about which model to use. I automatically route your tasks to the cheapest capable model, avoiding expensive Sonnet/Opus unless absolutely necessary.

---

## 🚀 Quick Start

```bash
# See what would be used for a task
router route "create a youtube shorts script"

# Force a specific tier
router l3    # Use Gemini 3.1 for content creation
router l4    # Use Kimi for debugging
router auto  # Return to automatic selection

# View cost comparison
router compare
```

---

## 📊 The 4-Tier System

| Tier | Cost | Best For | Models |
|------|------|----------|--------|
| **L1** | **FREE** | Status checks, file listings | `openrouter/free`, `nemotron:free` |
| **L2** | **$0.10/M** | Simple coding, scripts, fetching | `qwen3.5-9b`, `qwen3.5-flash` |
| **L3** | **$0.88/M** | Content creation, analysis ⭐ | `gemini-3.1-flash-lite` |
| **L4** | **$7.50/M** | Debugging, critical decisions | `kimi-k2.5` |

**Blocked (Too Expensive):** Sonnet 4.5, Opus 4.6, GPT-5.4 Pro

---

## 💡 How It Works

When you ask me something, I automatically classify it:

| You Say | Detected | Router Picks |
|---------|----------|--------------|
| "Check disk space" | L1 (Minimal) | Free tier |
| "Write a Python script" | L2 (Efficient) | Qwen 3.5 Flash |
| "Create YouTube Shorts script" | L3 (Content) | Gemini 3.1 Flash Lite |
| "Debug this complex error" | L4 (Critical) | Kimi K2.5 |

---

## 🎬 Real Examples

```bash
# L1 - FREE ($0.00)
router route "list files in workspace"
router route "check system status"
router route "heartbeat check"

# L2 - CHEAP ($0.10-0.16/M)
router route "write a script to fetch data"
router route "install a new package"
router route "configure cron job"

# L3 - MID ($0.88/M) ⭐ Your Sweet Spot
router route "create YouTube Shorts about batteries"
router route "analyze market trends"
router route "improve this script"

# L4 - PREMIUM ($7.50/M)
router route "debug why videos aren't uploading"
router route "fix this complex architecture issue"
router route "design the business strategy"
```

---

## 🔧 Manual Override

Sometimes you know better than the classifier:

```bash
router l1   # Force free models (quick checks)
router l2   # Force cheap models (coding)
router l3   # Force Gemini 3.1 (content - your preference!)
router l4   # Force Kimi (debugging - when things break)
router auto # Back to automatic
```

After running any `router` command, you'll need to start a new conversation (`/new`) for it to take effect.

---

## 💰 Cost Savings

**Before:** Always using Kimi K2.5
- 1M tokens = $7.50
- Daily usage: ~$5-10

**After:** Smart routing
- Most tasks use L2/L3: $0.10-0.88/M
- Only debug uses L4: $7.50/M
- **Savings: ~80-90% on typical days**

---

## 🚫 Blocked Models

These are intentionally excluded (too expensive):
- `anthropic/claude-opus-4.6` - $30/M
- `anthropic/claude-sonnet-4.5` - $3/M+
- `openai/gpt-5.4-pro` - $198/M
- `openai/gpt-5.4` - $17.50/M

**Emergency override:** If you really need one, tell me explicitly: "Use Opus for this critical task" and I'll use it (but warn you about cost).

---

## 📁 Files

- `model_router.json` - Configuration and tier definitions
- `model_router.py` - Classification logic
- `router` - CLI command

---

## ✨ Why This System?

1. **You don't think about models** - I pick the right one
2. **Costs stay low** - Free/cheap for 80% of tasks
3. **Quality when needed** - Kimi for debugging, Gemini 3.1 for content
4. **No wallet surprises** - Blocked expensive models by default
5. **Full control** - Override anytime with `router l3` etc.

**Your preference (Gemini 3.1) is L3** - perfect for YouTube content creation!
