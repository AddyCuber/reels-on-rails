#!/usr/bin/env python3
"""
One-shot migration: curate stories.json for the senior-US audience recovery.

Actions:
  1. Drop off-target titles entirely (workplace/startup framings the 55+ audience
     doesn't see themselves in).
  2. Mark already-uploaded titles as published so they're never picked again.
  3. Reorder so the senior-US "gold lane" (inheritance manipulation, caregiver
     theft, property/HOA, elder financial abuse, post-death secrets, church
     fraud, scams) publishes first.

Idempotent — running it again on already-curated data is a no-op.
"""

import json
from pathlib import Path

STORIES_FILE = Path(__file__).resolve().parent.parent / "stories.json"

# Titles to delete entirely — wrong demographic.
OFF_TARGET = {
    "She Opened My Business",
    "Denver Doesn't Need a Passport",
    "The Reviews That Never Happened",
    "He Used My Network To Raise Against Me",
}

# Titles already uploaded to YouTube (per the underperformer list).
# Mark published with a skip_reason so the rotation never picks them.
ALREADY_UPLOADED = {
    "What My Sister Called Junk",
    "She Published My Book",
}

# Genres that are senior-US bullseye → publish these first.
GOLD_GENRES = {
    "inheritance_manipulation",
    "caregiver_betrayal",
    "neighbor_property",
    "neighbor_hoa",
    "elder_financial_abuse",
    "secrets_after_death",
    "church_fraud",
    "elder_scam",
}


def main():
    data = json.loads(STORIES_FILE.read_text())
    stories = data["stories"]
    before = len(stories)

    # 1. Drop off-target.
    stories = [s for s in stories if s["title"] not in OFF_TARGET]

    # 2. Mark already-uploaded.
    for s in stories:
        if s["title"] in ALREADY_UPLOADED and not s.get("published"):
            s["published"] = True
            s["skip_reason"] = "already uploaded — kept for record"

    # 3. Reorder: gold genres first, then everything else, preserving order
    #    within each bucket so we don't shuffle randomly.
    gold = [s for s in stories if s.get("genre") in GOLD_GENRES]
    rest = [s for s in stories if s.get("genre") not in GOLD_GENRES]
    stories = gold + rest

    data["stories"] = stories
    STORIES_FILE.write_text(json.dumps(data, indent=2) + "\n")

    unpublished = [s for s in stories if not s.get("published")]
    print(f"Stories: {before} -> {len(stories)} ({before - len(stories)} dropped)")
    print(f"Unpublished pool: {len(unpublished)}")
    print(f"Marked already-uploaded: {sum(1 for s in stories if s.get('skip_reason'))}")
    print(f"Next up: {unpublished[0]['title']!r}")


if __name__ == "__main__":
    main()
