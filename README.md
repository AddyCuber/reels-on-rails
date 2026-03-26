# 🎬 Faceless Shorts Pipeline

Automated pipeline for generating viral faceless story shorts for YouTube Shorts and Instagram Reels.

**Stack:** stories.json → Edge TTS (voice) → Pexels (B-roll) → FFmpeg (edit) → Auto-upload

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

### Add more stories
Use the prompt in `scripts/generate_stories_prompt.txt` with Claude.ai and append the results to the `stories` array in `stories.json`.

---

## Cost Estimate

Per video:
- stories.json: $0.00 (static file)
- Edge TTS: $0.00 (free)
- Pexels: $0.00 (free)
- FFmpeg: $0.00 (local/CI)
- **Total: $0.00/video**

---

## Weekly Workflow

Stories are pre-written and stored in `stories.json`. Each run consumes the next story in order. When you run out, it loops.

To replenish the story queue:

1. Open [Claude.ai](https://claude.ai)
2. Paste the prompt from `scripts/generate_stories_prompt.txt`
3. Copy the JSON output
4. Replace the `stories` array in `stories.json` (keep `last_used_index` as `0`)
5. `git push` — GitHub Actions handles the rest

Also run weekly to keep Instagram auth alive:
```bash
python scripts/refresh_instagram_token.py --update-env
```

---

## First-Time YouTube Auth

YouTube requires a one-time OAuth flow to generate a refresh token. Do this locally before setting up GitHub Actions.

1. Download your `client_secrets.json` from [Google Cloud Console](https://console.cloud.google.com) (YouTube Data API v3 → OAuth 2.0 Client ID → Desktop app)
2. Run the auth script:
   ```bash
   python scripts/auth_youtube.py
   ```
3. Complete the browser OAuth flow — `youtube_token.json` is created locally
4. Base64-encode it:
   ```bash
   base64 -w0 youtube_token.json   # Linux
   base64 -i youtube_token.json    # macOS
   ```
5. Add the output as a GitHub Secret named `YOUTUBE_TOKEN`
   (Repo → Settings → Secrets and variables → Actions → New repository secret)

The GitHub Actions workflow automatically re-encodes and updates this secret after each run so the refreshed token persists.

---

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `PEXELS_API_KEY` | Pexels API key (free) |
| `YOUTUBE_CLIENT_SECRETS` | Contents of `client_secrets.json` |
| `YOUTUBE_TOKEN` | Base64-encoded `youtube_token.json` (from auth step above) |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Meta Graph API token (optional) |
| `INSTAGRAM_USER_ID` | Instagram business/creator account ID (optional) |
| `GH_TOKEN` | GitHub Personal Access Token with `repo` and `secrets` scope |

---

## Automation (cron job)

```bash
# Generate and upload 3 videos per day at 9am, 1pm, 6pm
0 9,13,18 * * * cd /path/to/faceless-shorts && python main.py >> logs/cron.log 2>&1
```
