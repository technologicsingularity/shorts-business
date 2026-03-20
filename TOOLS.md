# TOOLS.md - Local Notes

## Content Strategy

### Music Videos
- **Format:** Standard video
- **Aspect Ratio:** 16:9 (1920x1080)
- **Duration:** 3-5 minutes
- **Upload Type:** Regular video
- **Background:** Cinematic, wide shots

### "How It Works" Explainers  
- **Format:** YouTube Shorts
- **Aspect Ratio:** 9:16 (1080x1920)
- **Duration:** 50-60 seconds
- **Upload Type:** Shorts
- **Background:** Vertical, phone-optimized visuals

## TTS / Voice

### 🚨 CRITICAL: Voice ID Validation
- **PRIMARY VOICE:** Alita (ElevenLabs Voice ID: `IzvSBRjn2q72XdO9rbo8`)
  - Name: TS_Soft_Innocent
  - Cloned from Rosa Salazar's Alita Battle Angel performance
  - REMIXED: Softer, more approachable tone for explainers
  - 73 seconds of training data from 4 movie scenes
- **🚫 BLOCKED VOICE (NEVER USE):** Janet (Voice ID: `Pc1wcuuxmTb5FDmDgPjO`)
  - WRONG voice - delete any videos using this
  - Config file will reject this voice ID
- **Fallback:** "Rachel" (ElevenLabs) - only if Alita voice unavailable

### Voice Validation
- **Config file:** `/data/.openclaw/workspace/voice_config.json`
- **Validation script:** `/data/.openclaw/workspace/validate_before_create.py`
- **ALWAYS** run validation before generating TTS
- **NEVER** proceed if voice check fails

## Video Creation Workflow (UPDATED March 19, 2026)

### New Philosophy: Quality Over Quantity
- **Target:** 1-2 videos per day (was 6+)
- **Focus:** Retention optimization, fewer mistakes
- **Why:** Analytics show 9-24s avg view duration — rushing causes errors (wrong face overlay, mismatched images)

### DUAL-IMAGE Retention Strategy (NEW)
Based on analytics showing viewers drop off at 9-24s:

1. **Image 1** → Shows for **12 seconds** (establishes topic)
2. **Image 2** → Shows from **12s to end** (pattern interrupt to retain viewers)
3. **Hypothesis:** Visual switch right before typical drop-off extends retention

### Workflow Steps

1. **Script** → Write ~55 second explainer
2. **Audio** → Generate with TTS (check duration)
3. **Backgrounds** → Generate **TWO** images:
   - Image 1: Primary visual (topic hook)
   - Image 2: Secondary visual (different angle/style)
   - Both MUST be 9:16 aspect ratio
4. **VALIDATION** → Use new dual-image script:
   ```bash
   python3 create_video_dual.py bg1.png bg2.png face.mp4 audio.mp3 output.mp4
   ```
5. **Quality Check** → Verify before upload:
   - Face overlay in correct position (bottom right)
   - Image switch happens at 12s
   - No wrong images in wrong places
6. **Upload** → PUBLIC status for Shorts maximum reach

### Scripts

**Legacy (single image):**
```bash
python3 create_video.py shorts <bg> <face> <audio> <output>
```

**NEW (dual image - RECOMMENDED):**
```bash
python3 create_video_dual.py <bg1> <bg2> <face> <audio> <output>
```

**Options:**
- `--switch 12` - Change image at 12 seconds (default)
- `--dry-run` - Preview command without rendering
- `--single` - Fallback to single image mode

## Aspect Ratio Reference
- **9:16 (Shorts):** `--aspect-ratio 9:16` → 1080x1920
- **16:9 (Standard):** `--aspect-ratio 16:9` → 1920x1080

## Validation Checklist (UPDATED)

### Pre-Production
- [ ] **Check `completed_videos.md`** - Topic not already covered
- [ ] **Run validation script:** `python3 validate_before_create.py script.txt`
- [ ] **Verify voice ID** - Must be TS_Soft_Innocent (NOT Janet)
- [ ] **Generate TWO backgrounds** (for dual-image retention strategy)

### Production
- [ ] **DRY RUN first:** `python3 create_video_dual.py ... --dry-run`
- [ ] Correct aspect ratio (9:16 for Shorts)
- [ ] Audio duration checked (30-90s optimal)
- [ ] **VERIFY INPUT FILES** before rendering (prevent face/background mix-ups)

### Post-Production (CRITICAL - Don't Skip)
- [ ] **WATCH the video** before uploading (check for errors)
- [ ] Face overlay visible in bottom right (NOT replaced by random image)
- [ ] Image switch happens at ~12 seconds
- [ ] Video duration matches audio duration
- [ ] No visual glitches or wrong assets

### Upload
- [ ] Upload status = PUBLIC
- [ ] Video appears on channel after upload
- [ ] **Update `completed_videos.md`** with new video entry

## Duplicate Prevention
- **Tracker file:** `/data/.openclaw/workspace/completed_videos.md`
- **Check before creating** ANY video script
- Topics marked with ❌ are **NEVER** to be duplicated
- Topics marked with ⏳ are safe to use

## YouTube
- Channel: Technologic Singularity
- Email: technologicsingularity@gmail.com
- Upload script: `/data/.openclaw/workspace/youtube_upload.py`
- Token saved: ✅ Ready for auto-upload
- SEO Config: `/data/.openclaw/workspace/youtube_seo_config.json`

### Hashtags & SEO (NEW - March 18, 2026)

**Auto-generated for every upload:**
- Default tags: #howitworks #didyouknow #learnontiktok #edutok #science #technology #interestingfacts #facts
- Topic-specific tags based on video content (battery, airplane, gps, etc.)
- Keywords extracted from title
- Description template with hook + hashtags

**Usage:**
```bash
# Auto-generate hashtags based on topic
python3 youtube_upload.py <auth_code> \
  --title "Why Your Phone Battery Dies" \
  --topic battery \
  --status public

# Override with custom tags
python3 youtube_upload.py <auth_code> \
  --title "Custom Title" \
  --tags custom tag list here

# Test hashtag generation
python3 test_hashtags.py
```

**Available topics:** battery, fiber, ground_pin, airplane, speakers, smoke_detector, camera, refrigerator, microwave, keys, gps

**SEO Strategy:**
- 15 tags max (YouTube limit)
- Mix of broad (#Shorts #YouTubeShorts) and niche-specific tags
- Title keywords auto-extracted
- Description optimized for Shorts algorithm

## Assets
- Face video: looping GIF style (verify before each render — confirmed bug where wrong video was used)
- Background images: topic-specific, aspect-ratio matched

## Common Errors & Prevention

### Face Overlay Bug (FIXED PROCESS)
**Problem:** Purple sky image appeared instead of Alita's face in "How Touchscreens Work" video
**Cause:** Wrong input file passed to ffmpeg (face video variable contained image path)
**Prevention:** 
- New `create_video_dual.py` validates all inputs before rendering
- Explicit file type checking (rejects .png when .mp4 expected)
- DRY RUN mode to preview pipeline

### Image Mix-ups
**Problem:** Wrong background paired with wrong script
**Prevention:**
- Always verify file paths with `--dry-run` first
- Naming convention: `<topic>_bg1.png`, `<topic>_bg2.png`
- Single topic per work session (don't batch multiple topics)

### Retention Killers
From analytics (March 19, 2026):
| Video | Avg View | % Watched |
|-------|----------|-----------|
| Touchscreens | 9s | 50.6% |
| Newton's Cradle | 16s | 27.5% |
| QR Codes | 15s | 34.6% |
| Airplane Hole | 24s | 51.2% |

**Insight:** Switching visuals at 12s targets the 9-16s drop-off window

## Email Workflow (Updated March 18, 2026)

### Problem Identified
I was checking Gmail but only listing unread emails without taking action. Jordan pointed out:
- Emails were marked as read with no follow-up
- Bounced emails weren't tracked
- Responses weren't flagged for action

### New System
**Tracking Directory:** `/data/.openclaw/workspace/email_tracking/`

**Key Files:**
- `factories.json` - Factory contacts and response status
- `dead_emails.json` - Bounced/undeliverable addresses (NEVER contact again)
- `pending_responses.json` - Emails waiting for replies
- `received_responses.json` - Responses that need action

**Scripts:**
- `check_gmail_smart.py` - Reads content, categorizes, takes action
- `check_sent_emails.py` - Tracks what we sent
- `check_responses.py` - Finds replies to our emails
- `read_email.py` - Read specific email content

### When Checking Emails:
1. **READ** full content (not just subject)
2. **CATEGORIZE:** bounce | factory_response | reply | other
3. **TAKE ACTION:**
   - Bounce → Add to dead_emails.json
   - Factory response → Update factories.json, extract key info
   - Reply → Create follow-up task
4. **REPORT** findings with clear next steps

### Current Factory Contacts (Active)
| Company | Contact | Status | Next Action |
|---------|---------|--------|-------------|
| Dongguan Hucai Sportswear | Chris Nie | ✅ RESPONDED Mar 17 | Send tech packs for quote |

### Dead Email List (Do Not Contact)
*(Empty as of March 18 - no bounces detected yet)*
