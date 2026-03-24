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
    tts_voice: str = "en-US-ChristopherNeural"      # Deep male narrator voice
    tts_voice_female: str = "en-US-JennyNeural"     # Female alternative
    tts_rate: str = "+10%"                           # Slightly faster = more dramatic

    # ── Video Settings ────────────────────────────────────────────────────────
    video_width: int = 1080
    video_height: int = 1920   # 9:16 portrait for Shorts/Reels
    video_fps: int = 30
    video_bitrate: str = "4M"

    # ── Subtitle Style ────────────────────────────────────────────────────────
    subtitle_font: str = "Arial-Bold"
    subtitle_fontsize: int = 72
    subtitle_color: str = "white"
    subtitle_outline_color: str = "black"
    subtitle_outline_width: int = 4
    subtitle_words_per_chunk: int = 2   # How many words shown at once

    # ── Story Settings ────────────────────────────────────────────────────────
    story_max_duration: int = 55        # seconds (keep under 60 for Shorts)
    stories_file: str = "stories.json"

    # ── B-Roll Settings ───────────────────────────────────────────────────────
    broll_min_clip_duration: int = 3    # seconds per clip minimum
    broll_max_clip_duration: int = 8    # seconds per clip maximum

    # ── Upload Settings ───────────────────────────────────────────────────────
    upload_youtube: bool = True
    upload_instagram: bool = False      # Enable manually when ready
    youtube_category_id: str = "22"    # People & Blogs
    youtube_privacy: str = "public"    # public / private / unlisted
