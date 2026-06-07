#!/usr/bin/env python3
"""
Build a long-form compilation video from N stories in stories.json.

Long-form (>8 min) on YouTube unlocks mid-roll ads. For a senior-US audience
the CPM lift over Shorts is enormous (~$8–15 vs ~$0.05), so a single
compilation that gets even modest views outearns dozens of Shorts.

This reuses the existing TTS / B-roll / Editor agents to render each story
as a 1080x1920 segment, then concatenates the segments into one MP4 with
chapter timestamps for the YouTube description.

Usage:
    python scripts/compile_longform.py                                    # 5 most recent unpublished
    python scripts/compile_longform.py --count 6 --genre caregiver_betrayal
    python scripts/compile_longform.py --ids story_054,story_055,story_056
    python scripts/compile_longform.py --title "5 Inheritance Stories Where Justice Won"
    python scripts/compile_longform.py --mark-published   # mark stories as used after compile
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Make project root importable when running from anywhere.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.tts_agent import TTSAgent  # noqa: E402
from agents.broll_agent import BRollAgent  # noqa: E402
from agents.editor_agent import EditorAgent  # noqa: E402
from agents.uploader_agent import UploaderAgent  # noqa: E402
from agents.personality import PERSONALITIES  # noqa: E402
from config import Config  # noqa: E402


def select_stories(data: dict, count: int, genre: str | None, ids: list[str] | None) -> list[dict]:
    """Pick which stories to compile. Explicit --ids beats --genre beats default."""
    stories = data["stories"]

    if ids:
        wanted = list(ids)
        chosen = [s for s in stories if s.get("id") in wanted]
        missing = set(wanted) - {s.get("id") for s in chosen}
        if missing:
            raise SystemExit(f"ERROR: story IDs not found: {sorted(missing)}")
        return chosen

    pool = [s for s in stories if not s.get("published")]
    if genre:
        pool = [s for s in pool if s.get("genre") == genre]
    if len(pool) < count:
        raise SystemExit(
            f"ERROR: only {len(pool)} unpublished stor{'y' if len(pool)==1 else 'ies'} match"
            + (f" genre={genre!r}" if genre else "")
            + f", need {count}."
        )
    return pool[:count]


async def render_segment(
    story: dict,
    seg_dir: Path,
    config: Config,
    personality,
) -> tuple[Path, float]:
    """Render one story to a 1080x1920 segment. Returns (mp4_path, duration_sec)."""
    seg_dir.mkdir(parents=True, exist_ok=True)
    config.tts_voice = personality.voice

    tts = TTSAgent(config)
    narration = story["narration"]
    if story.get("hook"):
        narration = f"{story['hook']}.. {narration}"
    # Compilations don't get the per-Short follow CTA — single CTA at end of full video.
    audio_path, word_timings = await tts.synthesize(narration, seg_dir / "narration.mp3")

    duration = await tts.get_duration(audio_path)
    broll = BRollAgent(config)
    clips = await broll.fetch_clips(
        keywords=story["broll_keywords"],
        duration_needed=duration,
        output_dir=seg_dir / "clips",
        broll_category=personality.broll_category,
    )

    editor = EditorAgent(config, personality=personality)
    segment = await editor.compile(
        audio_path=audio_path,
        video_clips=clips,
        subtitles=word_timings,
        output_path=seg_dir / "segment.mp4",
    )
    return segment, duration


async def concat_segments(segments: list[Path], output_path: Path) -> Path:
    """Concat segment MP4s into one video. Re-encodes to avoid timebase mismatches."""
    list_file = output_path.parent / "concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in segments) + "\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed:\n{stderr.decode()[-1000:]}")
    return output_path


def _wrap_title(title: str, max_chars: int = 22) -> str:
    """Split title into lines of at most max_chars chars at word boundaries."""
    words = title.split()
    lines: list[str] = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = w
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


async def make_thumbnail(title: str, output: Path) -> Path:
    """Generate a 1280x720 thumbnail: dark background, big yellow wrapped title.

    Senior viewers tend to view on TVs and tablets — large legible text with
    high contrast outperforms anything cute. Yellow on near-black is the
    most-readable combo across age 60+ vision research.
    """
    text_file = output.with_suffix(".txt")
    text_file.write_text(_wrap_title(title))
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x0a0a14:s=1280x720",
        "-vf", (
            f"drawtext=textfile={text_file}"
            ":fontcolor=#FFD700:fontsize=88"
            ":x=(w-text_w)/2:y=(h-text_h)/2"
            ":line_spacing=18"
            ":borderw=5:bordercolor=black"
        ),
        "-frames:v", "1",
        str(output),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"thumbnail generation failed:\n{stderr.decode()[-500:]}")
    return output


def build_chapters(stories: list[dict], durations: list[float]) -> list[str]:
    """YouTube auto-detects chapters from `MM:SS Title` lines starting at 0:00."""
    chapters = []
    cursor = 0.0
    for story, dur in zip(stories, durations):
        m, s = divmod(int(cursor), 60)
        chapters.append(f"{m}:{s:02d} {story['title']}")
        cursor += dur
    return chapters


def mark_published(stories_file: Path, story_ids: list[str], compilation_id: str):
    data = json.loads(stories_file.read_text())
    now = datetime.now().isoformat(timespec="seconds")
    ids = set(story_ids)
    for s in data["stories"]:
        if s.get("id") in ids and not s.get("published"):
            s["published"] = True
            s["published_at"] = now
            s["compilation_id"] = compilation_id
    stories_file.write_text(json.dumps(data, indent=2) + "\n")


async def main():
    parser = argparse.ArgumentParser(description="Build a long-form story compilation")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--genre", help="Restrict to one genre (e.g. caregiver_betrayal)")
    parser.add_argument("--ids", help="Comma-separated story IDs (overrides count/genre)")
    parser.add_argument("--title", default=None, help="Compilation title (default: auto from genre)")
    parser.add_argument("--personality", type=int, default=0,
                        help=f"Personality index 0-{len(PERSONALITIES)-1} for the whole compilation")
    parser.add_argument("--mark-published", action="store_true",
                        help="Mark selected stories as published after a successful compile")
    parser.add_argument("--upload", action="store_true",
                        help="Upload to YouTube as long-form (private by default)")
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"],
                        help="YouTube privacy when --upload is set (default: private)")
    args = parser.parse_args()

    config = Config()
    stories_path = Path(config.stories_file)
    data = json.loads(stories_path.read_text())

    ids = [i.strip() for i in args.ids.split(",")] if args.ids else None
    selected = select_stories(data, args.count, args.genre, ids)
    personality = PERSONALITIES[args.personality % len(PERSONALITIES)]

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = PROJECT_ROOT / "output" / f"longform_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nCompiling {len(selected)} stories into a long-form video")
    print(f"  Voice: {personality.voice} | Layout: {personality.layout}")
    for s in selected:
        print(f"   • {s['id']}: {s['title']}")

    segments = []
    durations = []
    for i, story in enumerate(selected):
        print(f"\n[{i+1}/{len(selected)}] Rendering: {story['title']}")
        seg_path, dur = await render_segment(
            story, output_dir / f"seg_{i:02d}", config, personality
        )
        segments.append(seg_path)
        durations.append(dur)

    print("\nConcatenating segments...")
    final = output_dir / "longform.mp4"
    await concat_segments(segments, final)

    chapters = build_chapters(selected, durations)
    title = args.title or f"{len(selected)} {(args.genre or 'Senior US').replace('_', ' ').title()} Stories"

    print("Generating thumbnail...")
    thumbnail = await make_thumbnail(title, output_dir / "thumbnail.jpg")
    description = (
        f"{title}\n\n"
        "Chapters:\n" + "\n".join(chapters) + "\n\n"
        "All stories are fictional and for entertainment purposes only.\n"
        "Subscribe for new compilations every week."
    )
    (output_dir / "description.txt").write_text(description)
    (output_dir / "compilation_meta.json").write_text(json.dumps({
        "run_id": run_id,
        "title": title,
        "personality_index": args.personality,
        "story_ids": [s["id"] for s in selected],
        "chapter_lines": chapters,
        "total_seconds": sum(durations),
    }, indent=2))

    total_min = sum(durations) / 60
    print(f"\n✓ Compilation: {final}")
    print(f"  Duration: {total_min:.1f} min ({'eligible' if total_min >= 8 else 'BELOW 8 min — no mid-roll ads'})")
    print(f"  Description: {output_dir / 'description.txt'}")

    if args.upload:
        print(f"\nUploading to YouTube as long-form (privacy={args.privacy})...")
        uploader = UploaderAgent(config)
        # Long-form tags — no "shorts", focused on senior-US drama keywords.
        tags = ["story", "stories", "drama", "family drama", "true stories",
                "narrated stories", "compilation", args.genre or "stories"]
        result = await uploader.upload_youtube_longform(
            video_path=final,
            title=title,
            description=description,
            tags=tags,
            privacy=args.privacy,
            thumbnail_path=thumbnail,
        )
        if result["success"]:
            print(f"  ✓ Uploaded: {result['url']}")
            (output_dir / "compilation_meta.json").write_text(json.dumps({
                **json.loads((output_dir / "compilation_meta.json").read_text()),
                "youtube_url": result["url"],
                "youtube_video_id": result["video_id"],
            }, indent=2))
        else:
            print(f"  ✗ Upload failed: {result['error']}")
            print("  Stories will NOT be marked published since upload failed.")
            return

    if args.mark_published:
        mark_published(stories_path, [s["id"] for s in selected], run_id)
        print(f"\nMarked {len(selected)} stor{'y' if len(selected)==1 else 'ies'} as published.")
    else:
        print("\n  Stories left unpublished — they will still run as Shorts. Recommended for")
        print("  monetization: same story on both surfaces drives subs (Shorts) AND watch hours")
        print("  (compilation) without burning unique content. Pass --mark-published only if")
        print("  you want a compilation-exclusive story.")


if __name__ == "__main__":
    asyncio.run(main())
