"""
Pull top weekly posts from drama subreddits using Reddit's public JSON API.
No credentials required.
Run: python scripts/reddit_scraper.py
"""

import json
import time
from datetime import datetime, timezone

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 StoryDramaScraper/1.0"}

SUBREDDITS = [
    "AmItheAsshole",       # high-volume drama, scores regularly 5k-15k
    "TrueOffMyChest",      # personal confession drama
    "relationship_advice", # conflict/betrayal stories
    "EntitledParents",     # family entitlement drama
    "JUSTNOMIL",           # in-law conflict, reliable weekly posts
    "MaliciousCompliance", # revenge/workplace stories
    "survivinginfidelity", # betrayal/affair stories, first-person narrators
]

# Phrases that indicate the post is a third-party compilation, not the original narrator.
# These read poorly as TTS scripts and may duplicate stories from other subs.
THIRD_PARTY_PHRASES = (
    "i am not the oop",
    "i am not oop",
    "i am not op",
    "i'm not the oop",
    "i'm not oop",
    "not the original poster",
    "not the original op",
)

MIN_SCORE = 500
MIN_WORDS = 300
MAX_WORDS = 3000
OUTPUT_FILE = "story_candidates.json"
REQUEST_DELAY = 2  # seconds between subreddit requests to be polite


def word_count(text: str) -> int:
    return len(text.split())


def readable_date(utc_timestamp: float) -> str:
    return datetime.fromtimestamp(utc_timestamp, tz=timezone.utc).strftime("%Y-%m-%d")


def fetch_subreddit(subreddit: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=week&limit=25"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ERROR fetching r/{subreddit}: {e}")
        return []

    posts = resp.json().get("data", {}).get("children", [])
    candidates = []

    for child in posts:
        p = child.get("data", {})

        # Must be a self (text) post
        if not p.get("is_self"):
            continue
        # Skip NSFW
        if p.get("over_18"):
            continue
        # Skip deleted/removed
        body = p.get("selftext", "").strip()
        if not body or body in ("[deleted]", "[removed]"):
            continue
        author = p.get("author", "")
        if not author or author in ("[deleted]", "AutoModerator"):
            continue
        # Skip third-party compilation posts — not the original narrator, reads poorly as TTS
        body_lower = body[:200].lower()
        if any(phrase in body_lower for phrase in THIRD_PARTY_PHRASES):
            continue

        score = p.get("score", 0)
        if score < MIN_SCORE:
            continue

        wc = word_count(body)
        if not (MIN_WORDS <= wc <= MAX_WORDS):
            continue

        candidates.append({
            "title": p.get("title", "").strip(),
            "body": body,
            "score": score,
            "comments": p.get("num_comments", 0),
            "subreddit": subreddit,
            "url": "https://reddit.com" + p.get("permalink", ""),
            "word_count": wc,
            "scraped_date": readable_date(p.get("created_utc", 0)),
        })

    return candidates


def main() -> None:
    all_candidates = []

    for subreddit in SUBREDDITS:
        print(f"  r/{subreddit} …", end=" ", flush=True)
        results = fetch_subreddit(subreddit)
        print(f"{len(results)} found")
        all_candidates.extend(results)
        time.sleep(REQUEST_DELAY)

    all_candidates.sort(key=lambda p: p["score"], reverse=True)

    output = {
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_candidates": len(all_candidates),
        "stories": all_candidates,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_candidates)} candidates → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
