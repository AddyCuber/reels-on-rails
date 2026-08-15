#!/usr/bin/env python3
"""
Auto-generate stories using Gemini API when the unpublished queue drops below threshold.
Uses standard library urllib (zero external dependencies).
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

MIN_THRESHOLD = 5       # Trigger generation when fewer than 5 unpublished stories remain
BATCH_COUNT = 10         # How many new stories to generate when triggered
STORIES_FILE = Path("stories.json")
ARCHIVE_FILE = Path("stories_archive.json")
PROMPT_FILE = Path("scripts/generate_stories_prompt.txt")

GEMINI_MODEL = "gemini-2.5-flash"


def get_max_story_id() -> int:
    """Find the highest story_XXX index across stories.json and stories_archive.json."""
    max_id = 0
    for p in [STORIES_FILE, ARCHIVE_FILE]:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                stories = data.get("stories", []) if isinstance(data, dict) else data
                for s in stories:
                    sid = s.get("id", "")
                    if sid.startswith("story_"):
                        try:
                            num = int(sid.split("_")[1])
                            if num > max_id:
                                max_id = num
                        except ValueError:
                            pass
            except Exception:
                pass
    return max_id


def count_unpublished_stories() -> int:
    if not STORIES_FILE.exists():
        return 0
    try:
        data = json.loads(STORIES_FILE.read_text())
        stories = data.get("stories", [])
        return sum(1 for s in stories if not s.get("published"))
    except Exception:
        return 0


def call_gemini_api(api_key: str, prompt: str) -> list[dict]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.8
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            
        candidates = res_data.get("candidates", [])
        if not candidates:
            raise RuntimeError("No candidates returned from Gemini API")
            
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("No parts in Gemini response content")
            
        raw_text = parts[0].get("text", "").strip()
        parsed = json.loads(raw_text)
        
        if isinstance(parsed, dict) and "stories" in parsed:
            return parsed["stories"]
        elif isinstance(parsed, list):
            return parsed
        else:
            raise ValueError("Unexpected JSON format returned from Gemini")
            
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini API HTTP Error {e.code}: {err_body}")
    except Exception as e:
        raise RuntimeError(f"Gemini API Call failed: {e}")


def main():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[auto-generate] GEMINI_API_KEY is not set. Skipping auto-generation check.")
        return

    remaining = count_unpublished_stories()
    print(f"[auto-generate] Remaining unpublished stories: {remaining} (threshold: {MIN_THRESHOLD})")

    if remaining >= MIN_THRESHOLD:
        print("[auto-generate] Queue has sufficient stories. No generation needed.")
        return

    print(f"[auto-generate] Queue is low ({remaining} < {MIN_THRESHOLD}). Requesting {BATCH_COUNT} new stories from Gemini ({GEMINI_MODEL})...")
    
    start_id_num = get_max_story_id() + 1
    
    prompt_template = """Generate exactly {count} first-person dramatic short story scripts for YouTube Shorts and Instagram Reels targeting senior 60+ US audiences.

OUTPUT FORMAT:
Output a JSON array of objects.

STORY SCHEMA (each object in the array must contain these exact fields):
- title: string (specific, intriguing, max 60 chars)
- genre: string (one of: inheritance, business, hoa_neighbor, caregiver_theft, pension_scams, property_boundary_dispute, church_fraud)
- hook: string (1 sentence shocking opening statement, present tense)
- card_text: string (1-2 sentence teaser summary)
- narration: string (300-450 words full dramatic story text, including the hook as the first sentence)
- broll_keywords: array of 5-6 short visual phrase strings (e.g. ["legal document", "coffee cup", "police car"])
- hashtags: array of 5-6 hashtag strings (e.g. ["shorts", "storytime", "justice", "revenge"])
- description: string (2 sentence YouTube caption)
- estimated_duration: integer between 140 and 175

REQUIREMENTS:
- Story themes must feature elder justice, revenge against entitled relatives, dishonest contractors, fake wills, HOA corruption, pension scams, or boundary disputes.
- First person perspective. Narrator outsmarts villain legally or through foresight.
- Specific details: fake names, dollar amounts, time periods.
- High engagement pacing.
"""
    prompt = prompt_template.format(count=BATCH_COUNT)

    try:
        raw_stories = call_gemini_api(api_key, prompt)
        print(f"[auto-generate] Received {len(raw_stories)} story objects from Gemini API.")
    except Exception as e:
        print(f"[auto-generate] ERROR during Gemini generation: {e}", file=sys.stderr)
        sys.exit(1)

    # Process and format generated stories
    formatted_stories = []
    for i, s in enumerate(raw_stories):
        id_num = start_id_num + i
        sid = f"story_{id_num:03d}"
        
        story_obj = {
            "id": sid,
            "title": s.get("title", f"Story {id_num}"),
            "domain": s.get("genre", "general").replace("_", " ").title(),
            "genre": s.get("genre", "general"),
            "stayed_to_watch_target": "82%+",
            "card_text": s.get("card_text", s.get("description", "")),
            "hook": s.get("hook", ""),
            "villain_dismissal": s.get("villain_dismissal", "You can't stop me."),
            "reversal_type": s.get("reversal_type", "legal"),
            "proof_source": s.get("proof_source", "documents"),
            "witness_present": True,
            "narrator_position_at_end": "thriving",
            "narration": s.get("narration", ""),
            "broll_keywords": s.get("broll_keywords", ["legal document", "home interior", "coffee cup"]),
            "hashtags": s.get("hashtags", ["shorts", "storytime", "justice", "revenge"]),
            "description": s.get("description", ""),
            "estimated_duration": int(s.get("estimated_duration", 155))
        }
        formatted_stories.append(story_obj)

    # Load existing queue
    if STORIES_FILE.exists():
        data = json.loads(STORIES_FILE.read_text())
        existing = data.get("stories", [])
    else:
        data = {"stories": []}
        existing = []

    # Append new stories
    existing.extend(formatted_stories)
    data["stories"] = existing
    STORIES_FILE.write_text(json.dumps(data, indent=2))

    new_total = sum(1 for s in existing if not s.get("published"))
    print(f"[auto-generate] Successfully added {len(formatted_stories)} stories to {STORIES_FILE}. Total unpublished queue: {new_total}.")


if __name__ == "__main__":
    main()
