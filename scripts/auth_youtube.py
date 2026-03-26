#!/usr/bin/env python3
"""
One-time YouTube OAuth setup.

Run this locally to generate youtube_token.json, then base64-encode it
and store it as the YOUTUBE_TOKEN GitHub Secret.

Usage:
    python scripts/auth_youtube.py
    python scripts/auth_youtube.py --secrets path/to/client_secrets.json
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
import google.oauth2.credentials

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "youtube_token.json"


def main():
    parser = argparse.ArgumentParser(description="YouTube OAuth setup")
    parser.add_argument(
        "--secrets",
        default=os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json"),
        help="Path to client_secrets.json (default: client_secrets.json)",
    )
    parser.add_argument(
        "--token-out",
        default=TOKEN_FILE,
        help=f"Where to save the token (default: {TOKEN_FILE})",
    )
    args = parser.parse_args()

    secrets_path = Path(args.secrets)
    if not secrets_path.exists():
        print(f"ERROR: client secrets file not found: {secrets_path}")
        print(
            "\nTo get this file:\n"
            "  1. Go to console.cloud.google.com\n"
            "  2. New project -> Library -> Enable 'YouTube Data API v3'\n"
            "  3. Credentials -> Create OAuth 2.0 Client ID -> Desktop app\n"
            "  4. Download JSON and save it here\n"
        )
        raise SystemExit(1)

    print(f"Using client secrets: {secrets_path}")
    print("A browser window will open. Log in and authorize the app.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
    credentials = flow.run_local_server(port=0)

    token_path = Path(args.token_out)
    token_path.write_text(credentials.to_json())
    print(f"\nToken saved to: {token_path}")

    print("\nNext steps — add this token as a GitHub Secret:")
    print(f"  base64 -w0 {token_path}   # Linux")
    print(f"  base64 -i {token_path}    # macOS")
    print("  Then: GitHub repo -> Settings -> Secrets -> New secret")
    print("  Name: YOUTUBE_TOKEN   Value: <base64 output>")


if __name__ == "__main__":
    main()
