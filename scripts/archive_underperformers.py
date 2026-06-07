#!/usr/bin/env python3
"""
Set underperforming YouTube videos to private using existing OAuth token.

Reuses youtube_token.json produced by scripts/auth_youtube.py. Note that the
videos.update endpoint requires a broader scope than youtube.upload — if the
existing token only has upload scope, this script will print a clear error
and instruct you to re-run auth_youtube.py with the force-ssl scope.

Usage:
    python scripts/archive_underperformers.py
    python scripts/archive_underperformers.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


TOKEN_FILE = "youtube_token.json"

# Scopes that permit videos.update. youtube.upload alone is NOT enough.
WRITE_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

VIDEOS = [
    ("GfafPdIIq_4", "The Memo I Never Signed"),
    ("1TfJKdL9Kes", "She Published My Book"),
    ("v8t0dhPTwqo", "What My Sister Called Junk"),
    ("NzkFL7ilk_4", "He Used My Contacts To Fund His Startup"),
    ("ZR8AcCWbwwk", "He Put His Name On Every Slide"),
]


def load_credentials(token_path: Path) -> Credentials:
    if not token_path.exists():
        print(f"ERROR: token file not found at {token_path}")
        print("Run: python scripts/auth_youtube.py")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(str(token_path))

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json())

    granted = set(creds.scopes or [])
    if not granted.intersection(WRITE_SCOPES):
        print("ERROR: existing token does not have a scope that permits videos.update.")
        print(f"  Token scopes: {sorted(granted) or '(none)'}")
        print(f"  Required (one of): {WRITE_SCOPES}")
        print()
        print("Re-authorize with a broader scope by editing scripts/auth_youtube.py")
        print("to use SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']")
        print("then re-running it.")
        sys.exit(2)

    return creds


def set_private(youtube, video_id: str, title: str, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [dry-run] would set {video_id} ({title}) -> private")
        return True

    try:
        # Fetch existing snippet so update doesn't blank category/title metadata.
        resp = youtube.videos().list(part="status", id=video_id).execute()
        items = resp.get("items", [])
        if not items:
            print(f"  [skip]    {video_id} ({title}) — not found on this channel")
            return False

        current = items[0]["status"].get("privacyStatus")
        if current == "private":
            print(f"  [noop]    {video_id} ({title}) — already private")
            return True

        youtube.videos().update(
            part="status",
            body={
                "id": video_id,
                "status": {"privacyStatus": "private"},
            },
        ).execute()
        print(f"  [ok]      {video_id} ({title}) — {current} -> private")
        return True

    except HttpError as e:
        print(f"  [error]   {video_id} ({title}): {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Set underperforming videos to private")
    parser.add_argument(
        "--token",
        default=os.getenv("YOUTUBE_TOKEN_FILE", TOKEN_FILE),
        help=f"Path to OAuth token JSON (default: {TOKEN_FILE})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without applying")
    args = parser.parse_args()

    creds = load_credentials(Path(args.token))
    youtube = build("youtube", "v3", credentials=creds)

    print(f"Archiving {len(VIDEOS)} underperforming videos"
          + (" (dry run)" if args.dry_run else "") + ":")
    successes = 0
    for video_id, title in VIDEOS:
        if set_private(youtube, video_id, title, args.dry_run):
            successes += 1

    print(f"\nDone: {successes}/{len(VIDEOS)} processed successfully.")
    sys.exit(0 if successes == len(VIDEOS) else 1)


if __name__ == "__main__":
    main()
