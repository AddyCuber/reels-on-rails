# 🎬 Faceless Shorts Pipeline

Automated pipeline for generating viral faceless story shorts for YouTube Shorts and Instagram Reels.

**Stack:** Claude (story) → Edge TTS (voice) → Pexels (B-roll) → FFmpeg (edit) → Auto-upload

---

## Setup

### 1. Install system dependencies
```bash
# FFmpeg (required)
sudo apt install ffmpeg          # Ubuntu/Debian
brew install ffmpeg              # macOS

# Python 3.11+
python --version
```

### 2. Install Python packages
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

**Free API keys you need:**
| Service | Where to get | Cost |
|---------|-------------|------|
| Anthropic | console.anthropic.com | Pay-per-use (~$0.01/video) |
| Pexels | pexels.com/api | Free |
| Edge TTS | Built-in | Free |

### 4. YouTube Setup (one-time)
```bash
# 1. Go to console.cloud.google.com
# 2. New project → Library → Enable "YouTube Data API v3"
# 3. Credentials → Create OAuth 2.0 Client ID → Desktop app
# 4. Download JSON → save as client_secrets.json in this folder
# 5. First run will open a browser to authorize
```

### 5. Instagram Setup (one-time)
```bash
# 1. Your Instagram must be Business or Creator account
# 2. Connect it to a Facebook Page (required by Meta)
# 3. Go to developers.facebook.com → My Apps → Create App
# 4. Add product: Instagram Graph API
# 5. Generate a Long-lived Access Token (60 days, renewable)
# 6. Get your Instagram User ID from the API explorer
```

---

## Usage

```bash
# Generate 1 video (full pipeline)
python main.py

# Generate 5 videos in a row
python main.py --count 5

# Dry run (story + TTS + B-roll only, skip editing + upload)
python main.py --dry-run

# List available TTS voices
python -c "from agents.tts_agent import TTSAgent; TTSAgent.list_voices()"
```

---

## Output Structure

```
output/
└── 20240315_143022/
    ├── story.json          ← Generated script + metadata
    ├── narration.mp3       ← Edge TTS audio
    ├── subtitles.srt       ← Word-by-word subtitles
    ├── clips/              ← Downloaded B-roll clips
    │   ├── clip_000.mp4
    │   └── clip_001.mp4
    ├── tmp/                ← Intermediate files
    └── final.mp4           ← 🎬 Final 1080x1920 video
```

---

## Customization

### Change TTS voice
In `config.py`, change `tts_voice`. Run `python -c "from agents.tts_agent import TTSAgent; TTSAgent.list_voices()"` to see all options.

Best dramatic voices:
- `en-US-ChristopherNeural` — deep male, great for drama
- `en-GB-RyanNeural` — British authority
- `en-US-AriaNeural` — expressive female

### Change subtitle style
In `config.py`, tweak:
- `subtitle_fontsize` — bigger = more impactful
- `subtitle_words_per_chunk` — 1 for single word, 2-3 for phrases
- `subtitle_color` — white works best on mixed B-roll

### Add more story types
In `agents/story_agent.py`, add to `STORY_PROMPTS` and `BROLL_KEYWORD_POOLS`.

---

## Cost Estimate

Per video:
- Claude API: ~$0.01 (150 word story, Sonnet 3.5)
- Edge TTS: $0.00 (free)
- Pexels: $0.00 (free)
- FFmpeg: $0.00 (local)
- **Total: ~$0.01/video**

100 videos/month ≈ $1.00

---

## Automation (cron job)

```bash
# Generate and upload 3 videos per day at 9am, 1pm, 6pm
0 9,13,18 * * * cd /path/to/faceless-shorts && python main.py >> logs/cron.log 2>&1
```
