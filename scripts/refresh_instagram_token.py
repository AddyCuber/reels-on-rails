#!/usr/bin/env python3
"""
Refresh Instagram long-lived access token.

Instagram tokens last 60 days. Run this script weekly to reset the clock.

Usage:
    python scripts/refresh_instagram_token.py
    python scripts/refresh_instagram_token.py --update-env   # write new token back to .env
"""

import argparse
import os
import re
import sys
import urllib.request
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def refresh_token(token: str) -> dict:
    url = (
        "https://graph.facebook.com/oauth/access_token"
        f"?grant_type=ig_refresh_token&access_token={token}"
    )
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def update_env_file(new_token: str):
    env_path = Path(".env")
    if not env_path.exists():
        print("No .env file found — cannot update automatically.")
        return

    content = env_path.read_text()
    if "INSTAGRAM_ACCESS_TOKEN" in content:
        content = re.sub(
            r"^INSTAGRAM_ACCESS_TOKEN=.*$",
            f"INSTAGRAM_ACCESS_TOKEN={new_token}",
            content,
            flags=re.MULTILINE,
        )
    else:
        content += f"\nINSTAGRAM_ACCESS_TOKEN={new_token}\n"

    env_path.write_text(content)
    print(".env updated with new token.")


def main():
    parser = argparse.ArgumentParser(description="Refresh Instagram access token")
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Write the refreshed token back to .env automatically",
    )
    args = parser.parse_args()

    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    if not token:
        print("ERROR: INSTAGRAM_ACCESS_TOKEN not set in environment or .env")
        sys.exit(1)

    print("Refreshing Instagram token...")
    try:
        result = refresh_token(token)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    new_token = result.get("access_token", "")
    expires_in = result.get("expires_in", 0)
    token_type = result.get("token_type", "")

    print(f"\nNew token:   {new_token}")
    print(f"Token type:  {token_type}")
    print(f"Expires in:  {expires_in} seconds ({expires_in // 86400} days)")

    if args.update_env:
        update_env_file(new_token)
    else:
        print(
            "\nTo save this token, run with --update-env or paste it into your .env manually."
        )


if __name__ == "__main__":
    main()
