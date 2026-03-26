#!/usr/bin/env python3
"""
Faceless Shorts Pipeline - Orchestrator
Generates dramatic story shorts with B-roll, TTS, subtitles, and auto-upload.
"""

import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

from agents.tts_agent import TTSAgent
from agents.broll_agent import BRollAgent
from agents.editor_agent import EditorAgent
from agents.uploader_agent import UploaderAgent
from config import Config


def load_next_story(stories_file: str) -> tuple[dict, int]:
    """Read stories.json and return the next story plus its index."""
    data = json.loads(Path(stories_file).read_text())
    stories = data["stories"]
    index = data["last_used_index"] % len(stories)
    story = stories[index]

    total = len(stories)
    remaining = total - index - 1
    print(f"      Story #{index + 1}/{total}: \"{story['title']}\"")
    if remaining == 0:
        print(f"      (last story — will loop back to beginning on next run)")
    else:
        print(f"      ({remaining} stor{'y' if remaining == 1 else 'ies'} remaining before loop)")

    return story, index


def save_story_index(stories_file: str, used_index: int):
    """Increment last_used_index (with wrap) and write back to stories.json."""
    path = Path(stories_file)
    data = json.loads(path.read_text())
    next_index = (used_index + 1) % len(data["stories"])
    data["last_used_index"] = next_index
    path.write_text(json.dumps(data, indent=2))


async def run_pipeline(config: Config, dry_run: bool = False):
    print("\n FACELESS SHORTS PIPELINE STARTING\n" + "="*50)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"output/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load Story ───────────────────────────────────────────────────────────
    print("\n[1/5] Loading story from stories.json...")
    story, story_index = load_next_story(config.stories_file)
    story["word_count"] = len(story["narration"].split())
    print(f"      Words: {story['word_count']} | Genre: {story['genre']}")
    (output_dir / "story.json").write_text(json.dumps(story, indent=2))

    # ── Agent 2: Text-to-Speech ───────────────────────────────────────────────
    print("\n[2/5] Generating voiceover (Edge TTS)...")
    tts_agent = TTSAgent(config)
    audio_path, word_timings = await tts_agent.synthesize(
        text=story["narration"],
        output_path=output_dir / "narration.mp3"
    )
    # Use exact word timestamps from TTS — no estimation
    story["subtitle_chunks"] = word_timings
    print(f"      Audio saved: {audio_path} | {len(word_timings)} words timed")

    # ── Agent 3: Find B-Roll ─────────────────────────────────────────────────
    print("\n[3/5] Selecting B-roll footage (Pexels)...")
    broll_agent = BRollAgent(config)
    video_clips = await broll_agent.fetch_clips(
        keywords=story["broll_keywords"],
        duration_needed=story["estimated_duration"],
        output_dir=output_dir / "clips"
    )
    print(f"      Downloaded {len(video_clips)} clips")

    if dry_run:
        print("\n  DRY RUN — skipping video editing and upload")
        return story, audio_path, video_clips

    # ── Agent 4: Edit Video ───────────────────────────────────────────────────
    print("\n[4/5] Editing video with FFmpeg...")
    editor_agent = EditorAgent(config)
    final_video = await editor_agent.compile(
        audio_path=audio_path,
        video_clips=video_clips,
        subtitles=story["subtitle_chunks"],
        output_path=output_dir / "final.mp4"
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
    save_story_index(config.stories_file, story_index)
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

    asyncio.run(main())
