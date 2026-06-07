#!/usr/bin/env python3
"""
Faceless Shorts Pipeline - Orchestrator
Generates dramatic story shorts with B-roll, TTS, subtitles, and auto-upload.
"""

import asyncio
import argparse
import json
import random
from pathlib import Path
from datetime import datetime

from agents.tts_agent import TTSAgent
from agents.broll_agent import BRollAgent
from agents.editor_agent import EditorAgent
from agents.uploader_agent import UploaderAgent
from agents.personality import get_personality
from config import Config


def load_next_story(stories_file: str) -> tuple[dict, int]:
    """Return the next unpublished story and its index in the stories list.

    Hard-fails when every story has been published — we never silently repeat.
    Add new stories or clear `published` on a story to re-publish it.
    """
    data = json.loads(Path(stories_file).read_text())
    stories = data["stories"]
    total = len(stories)

    unpublished = [(i, s) for i, s in enumerate(stories) if not s.get("published")]
    if not unpublished:
        raise SystemExit(
            f"ERROR: all {total} stories in {stories_file} are marked published. "
            "Add new stories or unset 'published' on the ones you want to re-run."
        )

    index, story = unpublished[0]
    remaining = len(unpublished)
    print(f"      Story #{index + 1}/{total}: \"{story['title']}\"")
    print(f"      ({remaining} unpublished stor{'y' if remaining == 1 else 'ies'} remaining)")

    return story, index


def mark_story_published(stories_file: str, used_index: int):
    """Move the published story from stories.json to stories_archive.json."""
    queue_path = Path(stories_file)
    archive_path = queue_path.parent / "stories_archive.json"

    queue = json.loads(queue_path.read_text())
    story = queue["stories"].pop(used_index)
    story["published"] = True
    story["published_at"] = datetime.now().isoformat(timespec="seconds")
    queue_path.write_text(json.dumps(queue, indent=2))

    if archive_path.exists():
        archive = json.loads(archive_path.read_text())
    else:
        archive = {"stories": []}
    archive["stories"].append(story)
    archive_path.write_text(json.dumps(archive, indent=2))


async def run_pipeline(config: Config, dry_run: bool = False):
    print("\n FACELESS SHORTS PIPELINE STARTING\n" + "="*50)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"output/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load Story ───────────────────────────────────────────────────────────
    print("\n[1/5] Loading story from stories.json...")
    story, story_index = load_next_story(config.stories_file)
    story["word_count"] = len(story["narration"].split())

    # ── Pick Personality ─────────────────────────────────────────────────────
    personality = get_personality(story_index)
    print(f"      Words: {story['word_count']} | Genre: {story['genre']}")
    print(f"      Personality: {personality.voice} | {personality.layout} | {personality.broll_category}")
    (output_dir / "story.json").write_text(json.dumps(story, indent=2))

    # ── Agent 2: Text-to-Speech ───────────────────────────────────────────────
    print("\n[2/5] Generating voiceover (Edge TTS)...")
    config.tts_voice = personality.voice
    config.subtitle_style = random.choice(config.subtitle_styles)
    tts_agent = TTSAgent(config)
    narration_text = story["narration"]
    if story.get("hook"):
        narration_text = f"{story['hook']}.. {narration_text}"
    narration_text = f"{narration_text} Follow for a new story every day."
    audio_path, word_timings = await tts_agent.synthesize(
        text=narration_text,
        output_path=output_dir / "narration.mp3"
    )
    # Use exact word timestamps from TTS — no estimation
    story["subtitle_chunks"] = word_timings
    print(f"      Audio saved: {audio_path} | {len(word_timings)} words timed")

    # ── Agent 3: Find B-Roll ─────────────────────────────────────────────────
    print("\n[3/5] Selecting B-roll footage (Pexels)...")
    actual_duration = await tts_agent.get_duration(audio_path)
    broll_agent = BRollAgent(config)
    video_clips = await broll_agent.fetch_clips(
        keywords=story["broll_keywords"],
        duration_needed=actual_duration,
        output_dir=output_dir / "clips",
        broll_category=personality.broll_category,
    )
    print(f"      Downloaded {len(video_clips)} clips")

    if dry_run:
        print("\n  DRY RUN — skipping video editing and upload")
        return story, audio_path, video_clips

    # ── Agent 4: Edit Video ───────────────────────────────────────────────────
    print("\n[4/5] Editing video with FFmpeg...")
    editor_agent = EditorAgent(config, personality=personality)
    final_video = await editor_agent.compile(
        audio_path=audio_path,
        video_clips=video_clips,
        subtitles=story["subtitle_chunks"],
        output_path=output_dir / "final.mp4",
        card_text=story.get("card_text", ""),
    )
    print(f"      Final video: {final_video}")

    # ── Agent 5: Upload ───────────────────────────────────────────────────────
    print("\n[5/5] Uploading to platforms...")
    uploader = UploaderAgent(config)
    results = await uploader.upload_all(
        video_path=final_video,
        title=story["title"],
        description=story["description"],
        hashtags=story["hashtags"]
    )
    for platform, result in results.items():
        status = "OK" if result["success"] else "FAIL"
        print(f"      [{status}] {platform}: {result.get('url', result.get('error', ''))}")

    # ── Save progress ─────────────────────────────────────────────────────────
    if any(r.get("success") for r in results.values()):
        mark_story_published(config.stories_file, story_index)
    else:
        print("      ⚠️  No platform uploads succeeded — story stays unpublished and will retry next run")
        
    # Log results to CSV
    log_csv_path = Path("upload_log.csv")
    if not log_csv_path.exists():
        log_csv_path.write_text("timestamp,story_id,story_title,youtube_url,instagram_status,facebook_status,niche,video_duration,word_count,layout\n")
    
    # Calculate video duration securely
    try:
        vid_duration = await EditorAgent._get_duration(final_video)
    except:
        vid_duration = 0.0
        
    youtube_url = results.get("YouTube Shorts", {}).get("url", "")
    instagram_status = "OK" if results.get("Instagram Reels", {}).get("success") else results.get("Instagram Reels", {}).get("error", "SKIP")
    facebook_status = "OK" if results.get("Facebook Reels", {}).get("success") else results.get("Facebook Reels", {}).get("error", "SKIP")
    
    with open(log_csv_path, "a") as f:
        f.write(f"{datetime.now().isoformat()},{story.get('id', story_index)},\"{story['title']}\",{youtube_url},\"{instagram_status}\",\"{facebook_status}\",{story.get('niche', 'standard')},{vid_duration:.1f},{story['word_count']},{personality.layout}\n")

    print(f"\n PIPELINE COMPLETE — Output: {output_dir}\n")
    return final_video


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Faceless Shorts Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Skip editing and upload")
    parser.add_argument("--count", type=int, default=1, help="Number of videos to generate")
    args = parser.parse_args()

    config = Config()

    async def main():
        for i in range(args.count):
            if args.count > 1:
                print(f"\n{'='*50}\nGenerating video {i+1}/{args.count}\n{'='*50}")
            await run_pipeline(config, dry_run=args.dry_run)
            # Delay between videos to spread uploads across a natural window
            if args.count > 1 and i < args.count - 1:
                delay_minutes = random.randint(60, 180)
                print(f"\nWaiting {delay_minutes} minutes before next video...")
                await asyncio.sleep(delay_minutes * 60)

    asyncio.run(main())
