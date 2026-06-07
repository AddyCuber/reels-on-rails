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
import random
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
        # Random jitter to vary upload times
        jitter_max = getattr(self.config, 'upload_jitter_max_seconds', 5400)
        jitter = random.randint(0, jitter_max) if jitter_max > 0 else 0
        if jitter > 0:
            print(f"      Upload jitter: waiting {jitter // 60}m {jitter % 60}s before uploading...")
            await asyncio.sleep(jitter)

        tasks = {}
        results = {}

        if self.config.upload_youtube and self.config.youtube_client_secrets:
            tasks["YouTube Shorts"] = self._upload_youtube(video_path, title, description, hashtags)

        if self.config.upload_instagram and self.config.instagram_access_token:
            tasks["Instagram Reels"] = self._upload_instagram(video_path, title, description, hashtags)
            
        if self.config.upload_facebook and self.config.facebook_access_token:
            tasks["Facebook Reels"] = self._upload_facebook(video_path, title, description, hashtags)

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

    # ── YouTube long-form (compilations) ──────────────────────────────────────
    async def upload_youtube_longform(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
        privacy: str = "private",
        category_id: str | None = None,
        thumbnail_path: Path | None = None,
    ) -> dict:
        """Upload a long-form compilation (8+ min for mid-roll eligibility).

        Distinct from Shorts upload — no #Shorts hashtag, no Shorts tags, and
        the canonical URL is /watch?v=. Default privacy is private so you can
        review chapters/thumbnails before flipping to public.
        """
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import os

            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            TOKEN_FILE = "youtube_token.json"

            creds = None
            if os.path.exists(TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())
            if not creds or not creds.valid:
                return {"success": False, "error": "No valid YouTube credentials. Run scripts/auth_youtube.py first."}

            youtube = build("youtube", "v3", credentials=creds)
            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:30],
                    "categoryId": category_id or self.config.youtube_category_id,
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": False,
                    "containsSyntheticMedia": True,
                },
            }
            media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
            loop = asyncio.get_event_loop()
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = await loop.run_in_executor(None, request.execute)
            video_id = response.get("id")

            thumbnail_uploaded = False
            if thumbnail_path and Path(thumbnail_path).exists():
                try:
                    thumb_media = MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
                    thumb_req = youtube.thumbnails().set(videoId=video_id, media_body=thumb_media)
                    await loop.run_in_executor(None, thumb_req.execute)
                    thumbnail_uploaded = True
                except Exception as thumb_err:
                    # Channel may not be verified — videos.insert succeeds but thumbnails.set
                    # requires phone-verified channels. Don't fail the whole upload for this.
                    print(f"      ⚠️  Thumbnail upload failed (channel may need verification): {thumb_err}")

            return {
                "success": True,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
                "thumbnail_uploaded": thumbnail_uploaded,
            }
        except ImportError:
            return {"success": False, "error": "Missing google-api-python-client"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── YouTube Shorts ────────────────────────────────────────────────────────
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
            from google.auth.transport.requests import Request

            creds = None
            if os.path.exists(TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())
            elif not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.youtube_client_secrets, SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())

            youtube = build("youtube", "v3", credentials=creds)

            # Add #Shorts to title for YouTube to classify it
            yt_title = f"{title} #Shorts"
            yt_description = (
                description + "\n\n"
                "▶ Subscribe for a new story every day. Hit the bell so you never miss one.\n\n"
                + " ".join(f"#{tag}" for tag in hashtags) + " #Shorts"
                + "\n\nAll stories are fictional and for entertainment purposes only."
            )

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
                    "containsSyntheticMedia": True,
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
                video_url = await self.upload_to_file_host(video_path)

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

    # ── Facebook Reels ────────────────────────────────────────────────────────
    async def _upload_facebook(self, video_path: Path, title: str, description: str, hashtags: list[str]) -> dict:
        """
        Upload to Facebook Reels via Meta Graph API.
        Requires: Facebook Page ID + Access Token.
        """
        try:
            caption = f"{title}\n\n{description}\n\n" + " ".join(f"#{tag}" for tag in hashtags)
            caption = caption[:2200]  # Facebook caption limit might be different, keeping safe
            
            async with aiohttp.ClientSession() as session:
                # Step 1: Init Upload
                init_url = f"https://graph.facebook.com/v19.0/{self.config.facebook_page_id}/video_reels"
                init_data = {
                    "upload_phase": "start",
                    "access_token": self.config.facebook_access_token,
                }
                async with session.post(init_url, data=init_data) as resp:
                    data = await resp.json()
                    if "video_id" not in data:
                        return {"success": False, "error": f"Init failed: {data}"}
                    video_id = data["video_id"]
                    
                # Step 2: Transfer Upload
                transfer_url = "https://graph.facebook.com/v19.0/video_reels"
                with open(video_path, "rb") as f:
                    # Using aiohttp multipart data
                    form = aiohttp.FormData()
                    form.add_field("upload_phase", "transfer")
                    form.add_field("access_token", self.config.facebook_access_token)
                    form.add_field("video_id", video_id)
                    form.add_field("video_file_chunk", f, filename=video_path.name)
                    
                    async with session.post(transfer_url, data=form) as resp:
                        data = await resp.json()
                        if "success" not in data or not data["success"]:
                            return {"success": False, "error": f"Transfer failed: {data}"}
                            
                # Step 3: Finish Upload
                finish_url = f"https://graph.facebook.com/v19.0/{self.config.facebook_page_id}/video_reels"
                finish_data = {
                    "upload_phase": "finish",
                    "access_token": self.config.facebook_access_token,
                    "video_id": video_id,
                    "video_state": "PUBLISHED",
                    "description": caption,
                }
                async with session.post(finish_url, data=finish_data) as resp:
                    data = await resp.json()
                    if "success" in data and data["success"]:
                        return {"success": True, "video_id": video_id, "url": f"https://facebook.com/reel/{video_id}"}
                    else:
                        return {"success": False, "error": f"Finish failed: {data}"}

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

    async def upload_to_file_host(self, video_path: Path) -> str | None:
        """
        Upload video to tmpfiles.org to get a public URL for Instagram.
        Returns the direct download URL.
        """
        try:
            url = "https://tmpfiles.org/api/v1/upload"
            async with aiohttp.ClientSession() as session:
                with open(video_path, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field("file", f, filename=video_path.name)
                    
                    async with session.post(url, data=form, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("status") == "success":
                                # tmpfiles.org returns a view page URL like https://tmpfiles.org/12345/file.mp4
                                # To get the direct download link, we inject '/dl/' after the domain
                                view_url = data["data"]["url"]
                                direct_url = view_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                                return direct_url
        except Exception as e:
            print(f"      ⚠️  File host upload failed: {e}")
        return None
