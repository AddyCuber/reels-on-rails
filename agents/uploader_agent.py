"""
Agent 5: Uploader
Handles auto-upload to:
- YouTube Shorts (via YouTube Data API v3)
- Instagram Reels (via Meta Graph API)

Setup instructions are in README.md
"""

import asyncio
import aiohttp
import aiofiles
import json
from pathlib import Path
from config import Config


class UploaderAgent:
    def __init__(self, config: Config):
        self.config = config

    async def upload_all(
        self,
        video_path: Path,
        title: str,
        description: str,
        hashtags: list[str]
    ) -> dict:
        """Upload to all configured platforms concurrently."""
        tasks = {}
        results = {}

        if self.config.upload_youtube and self.config.youtube_client_secrets:
            tasks["YouTube Shorts"] = self._upload_youtube(video_path, title, description, hashtags)

        if self.config.upload_instagram and self.config.instagram_access_token:
            tasks["Instagram Reels"] = self._upload_instagram(video_path, title, description, hashtags)

        if not tasks:
            print("      ⚠️  No upload platforms configured. Set API keys in .env")
            return {}

        # Run uploads concurrently
        for platform, coro in tasks.items():
            try:
                result = await coro
                results[platform] = result
            except Exception as e:
                results[platform] = {"success": False, "error": str(e)}

        return results

    # ── YouTube ────────────────────────────────────────────────────────────────
    async def _upload_youtube(self, video_path: Path, title: str, description: str, hashtags: list[str]) -> dict:
        """Upload to YouTube using the Data API v3 with resumable upload."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import os

            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            TOKEN_FILE = "youtube_token.json"

            # Load or create credentials
            creds = None
            if os.path.exists(TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.youtube_client_secrets, SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())

            youtube = build("youtube", "v3", credentials=creds)

            # Add #Shorts to title for YouTube to classify it
            yt_title = f"{title} #Shorts"
            yt_description = description + "\n\n" + " ".join(f"#{tag}" for tag in hashtags) + " #Shorts"

            body = {
                "snippet": {
                    "title": yt_title[:100],
                    "description": yt_description[:5000],
                    "tags": hashtags + ["shorts", "story", "drama"],
                    "categoryId": self.config.youtube_category_id,
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": self.config.youtube_privacy,
                    "selfDeclaredMadeForKids": False,
                }
            }

            media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)

            # Run sync YouTube API call in thread pool
            loop = asyncio.get_event_loop()
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = await loop.run_in_executor(None, request.execute)

            video_id = response.get("id")
            return {
                "success": True,
                "url": f"https://youtube.com/shorts/{video_id}",
                "video_id": video_id
            }

        except ImportError:
            return {
                "success": False,
                "error": "Missing packages. Run: pip install google-auth google-auth-oauthlib google-api-python-client"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Instagram Reels ────────────────────────────────────────────────────────
    async def _upload_instagram(self, video_path: Path, title: str, description: str, hashtags: list[str]) -> dict:
        """
        Upload to Instagram Reels via Meta Graph API.
        Requires: Business/Creator account + Instagram Graph API access.
        
        Flow:
        1. Upload video to a hosting URL (we use a temp Imgur-style upload)
        2. Create media container
        3. Publish container
        """
        try:
            caption = f"{title}\n\n{description}\n\n" + " ".join(f"#{tag}" for tag in hashtags)
            caption = caption[:2200]  # Instagram caption limit

            async with aiohttp.ClientSession() as session:
                # Step 1: Upload video to get a publicly accessible URL
                # Note: Instagram requires a publicly accessible video URL.
                # In production, upload to your own server, S3, or similar.
                video_url = await self._upload_to_temp_host(session, video_path)

                if not video_url:
                    return {"success": False, "error": "Could not upload video to temp host. Configure a hosting solution."}

                # Step 2: Create media container
                container_url = f"https://graph.facebook.com/v19.0/{self.config.instagram_user_id}/media"
                container_data = {
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption,
                    "share_to_feed": "true",
                    "access_token": self.config.instagram_access_token,
                }
                async with session.post(container_url, data=container_data) as resp:
                    data = await resp.json()
                    if "id" not in data:
                        return {"success": False, "error": f"Container creation failed: {data}"}
                    container_id = data["id"]

                # Step 3: Wait for processing
                await self._wait_for_instagram_processing(session, container_id)

                # Step 4: Publish
                publish_url = f"https://graph.facebook.com/v19.0/{self.config.instagram_user_id}/media_publish"
                publish_data = {
                    "creation_id": container_id,
                    "access_token": self.config.instagram_access_token,
                }
                async with session.post(publish_url, data=publish_data) as resp:
                    data = await resp.json()
                    if "id" in data:
                        return {"success": True, "url": f"https://instagram.com/p/{data['id']}", "media_id": data["id"]}
                    else:
                        return {"success": False, "error": f"Publish failed: {data}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _wait_for_instagram_processing(self, session: aiohttp.ClientSession, container_id: str, max_wait: int = 120):
        """Poll Instagram until video processing is complete."""
        url = f"https://graph.facebook.com/v19.0/{container_id}"
        params = {"fields": "status_code", "access_token": self.config.instagram_access_token}

        for _ in range(max_wait // 5):
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                status = data.get("status_code", "")
                if status == "FINISHED":
                    return
                elif status == "ERROR":
                    raise RuntimeError(f"Instagram processing error: {data}")
            await asyncio.sleep(5)

    async def _upload_to_temp_host(self, session: aiohttp.ClientSession, video_path: Path) -> str | None:
        """
        Upload video to get a public URL for Instagram.
        
        OPTIONS (pick one based on your setup):
        A) Your own server/VPS — just serve from /var/www/uploads
        B) AWS S3 presigned URL
        C) Cloudinary (free tier available)
        D) Transfer.sh (simple but temp)
        
        This example uses transfer.sh for simplicity.
        For production, replace with S3 or your own server.
        """
        try:
            filename = video_path.name
            async with aiofiles.open(video_path, "rb") as f:
                video_data = await f.read()

            async with session.put(
                f"https://transfer.sh/{filename}",
                data=video_data,
                headers={"Max-Days": "1"},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    return (await resp.text()).strip()
        except Exception as e:
            print(f"      ⚠️  Temp upload failed: {e}")
        return None
