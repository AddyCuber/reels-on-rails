"""
Configuration — fill in your API keys here or use a .env file
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # ── API Keys ──────────────────────────────────────────────────────────────
    pexels_api_key: str = field(default_factory=lambda: os.getenv("PEXELS_API_KEY", ""))

    # YouTube (OAuth2 — see README for setup)
    youtube_client_secrets: str = field(default_factory=lambda: os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json"))

    # Instagram / Meta Graph API
    instagram_access_token: str = field(default_factory=lambda: os.getenv("INSTAGRAM_ACCESS_TOKEN", ""))
    instagram_user_id: str = field(default_factory=lambda: os.getenv("INSTAGRAM_USER_ID", ""))

    # ── TTS Settings ──────────────────────────────────────────────────────────
    # Run: edge-tts --list-voices | grep en-US   to see all options
    tts_voice: str = "en-US-ChristopherNeural"      # Set per-run by main.py
    tts_voices: list = field(default_factory=lambda: [
        "en-US-ChristopherNeural",   # Deep male — serious drama
        "en-GB-RyanNeural",          # British male — authority
        "en-US-AndrewNeural",        # Warm male — relatable
    ])
    tts_rate: str = "+55%"  # e.g., '+20%', '-10%', '+55%'                     # Fast pacing to hold attention
    tts_pitch: str = "+20Hz" # Higher pitch as requested
    tts_voice_alt: str = "en-US-AnaNeural"           # Alternate voice option

    # ── Video Settings ────────────────────────────────────────────────────────
    video_width: int = 1080
    video_height: int = 1920   # 9:16 portrait for Shorts/Reels
    video_fps: int = 30
    video_bitrate: str = "4M"

    # ── Subtitle Style ────────────────────────────────────────────────────────
    subtitle_font: str = "Impact"
    subtitle_fontsize: int = 90
    subtitle_outline_width: int = 5
    subtitle_styles: list = field(default_factory=lambda: [
        {"color": "&H00FFFFFF", "outline": "&H00000000"},  # white text, black outline
        {"color": "&H0000FFFF", "outline": "&H00000000"},  # yellow text, black outline
        {"color": "&H0000D7FF", "outline": "&H00000000"},  # orange text, black outline
    ])

    # ── Pipeline Control ──────────────────────────────────────────────────────
    upload_interval_hours: int = 4                   # How often to run loop mode
    # Random delay before uploading (default 90 mins). Override with the
    # UPLOAD_JITTER_MAX_SECONDS env var (e.g. 0 for manual test runs).
    upload_jitter_max_seconds: int = field(
        default_factory=lambda: int(os.getenv("UPLOAD_JITTER_MAX_SECONDS") or 5400)
    )

    # ── Story Settings ────────────────────────────────────────────────────────
    story_max_duration: int = 180       # seconds (target story word count is now 600-700 words)
    stories_file: str = "stories.json"

    # ── B-Roll Settings ───────────────────────────────────────────────────────
    broll_max_clip_duration: int = 8    # seconds per clip maximum

    # ── Upload Settings ───────────────────────────────────────────────────────
    upload_youtube: bool = True
    upload_instagram: bool = True      # Enable manually when ready
    
    # Facebook
    facebook_page_id: str = field(default_factory=lambda: os.getenv("FACEBOOK_PAGE_ID", ""))
    facebook_access_token: str = field(default_factory=lambda: os.getenv("FACEBOOK_ACCESS_TOKEN", ""))
    upload_facebook: bool = True
    youtube_category_id: str = "22"    # People & Blogs
    youtube_privacy: str = "public"    # public / private / unlisted
