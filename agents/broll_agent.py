"""
Agent 3: B-Roll Fetcher
Uses the Pexels API (free) to find and download relevant video clips.
Sign up free at pexels.com/api — no credit card needed.
"""

import asyncio
import aiohttp
import aiofiles
import random
from pathlib import Path
from config import Config


PEXELS_VIDEO_API = "https://api.pexels.com/v1/videos/search"

# Fallback keywords if specific ones return no results
FALLBACK_KEYWORDS = [
    "nature landscape", "city street", "forest walking",
    "ocean waves", "rain window", "sunrise morning",
    "coffee shop", "driving highway", "fireplace",
    "empty road", "clouds sky", "river stream"
]


class BRollAgent:
    def __init__(self, config: Config):
        self.config = config

    async def fetch_clips(
        self,
        keywords: list[str],
        duration_needed: float,
        output_dir: Path
    ) -> list[Path]:
        """Download enough B-roll clips to cover the video duration."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Shuffle keywords for variety
        random.shuffle(keywords)

        clips = []
        total_duration = 0.0
        clip_idx = 0

        async with aiohttp.ClientSession() as session:
            for keyword in keywords + FALLBACK_KEYWORDS:
                if total_duration >= duration_needed + 20:  # buffer for longer stories
                    break

                videos = await self._search_videos(session, keyword, per_page=10)
                if not videos:
                    continue

                # Pick 2-3 random clips per keyword to reduce repetition
                picks = random.sample(videos, min(3, len(videos)))
                download_tasks = []
                pick_meta = []
                for video in picks:
                    video_url = self._pick_quality(video, target_width=1080)
                    if not video_url:
                        continue
                    clip_path = output_dir / f"clip_{clip_idx:03d}.mp4"
                    download_tasks.append(self._download(session, video_url, clip_path))
                    pick_meta.append((clip_path, video, keyword))
                    clip_idx += 1

                results = await asyncio.gather(*download_tasks)
                for downloaded, (clip_path, video, kw) in zip(results, pick_meta):
                    if downloaded:
                        clips.append(clip_path)
                        clip_duration = min(video.get("duration", 6), self.config.broll_max_clip_duration)
                        total_duration += clip_duration
                        print(f"      ✓ '{kw}' → {clip_path.name} ({clip_duration}s)")

        if not clips:
            raise RuntimeError("No B-roll clips downloaded. Check your PEXELS_API_KEY.")

        return clips

    async def _search_videos(self, session: aiohttp.ClientSession, query: str, per_page: int = 5) -> list:
        """Search Pexels for videos matching a keyword."""
        headers = {"Authorization": self.config.pexels_api_key}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "portrait",   # 9:16 portrait clips preferred
            "size": "medium"
        }

        try:
            async with session.get(PEXELS_VIDEO_API, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("videos", [])
                elif resp.status == 401:
                    raise RuntimeError("Invalid Pexels API key. Get one free at pexels.com/api")
                else:
                    return []
        except asyncio.TimeoutError:
            print(f"      ⚠️  Timeout searching '{query}'")
            return []

    def _pick_quality(self, video: dict, target_width: int = 1080) -> str | None:
        """Pick the best video file URL for our target resolution."""
        files = video.get("video_files", [])
        if not files:
            return None

        # Sort by how close width is to target
        portrait_files = [f for f in files if f.get("quality") in ("hd", "sd")]

        if not portrait_files:
            portrait_files = files

        # Prefer portrait (height > width) or closest to target width
        portrait_files.sort(key=lambda f: abs(f.get("width", 0) - target_width))
        return portrait_files[0].get("link")

    async def _download(self, session: aiohttp.ClientSession, url: str, path: Path) -> bool:
        """Download a video file."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    async with aiofiles.open(path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)
                    return True
        except Exception as e:
            print(f"      ⚠️  Download failed: {e}")
        return False
