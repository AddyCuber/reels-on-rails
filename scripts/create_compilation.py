"""
Create a long-form YouTube compilation from top-performing Shorts.
Reads upload_log.csv, finds local output folders, normalizes clips,
adds title cards and fades, then concatenates into one video.

Usage:
    python scripts/create_compilation.py
    python scripts/create_compilation.py --top 3
    python scripts/create_compilation.py --dry-run
"""

import argparse
import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("upload_log.csv")
OUTPUT_DIR = Path("output/compilation")
TMP_DIR = OUTPUT_DIR / "tmp"
FINAL_OUTPUT = OUTPUT_DIR / "compilation.mp4"
METADATA_FILE = OUTPUT_DIR / "metadata.txt"

CHANNEL_NAME = "Short Stories Drama"


# ─── helpers ──────────────────────────────────────────────────────────────────

def check_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ERROR: ffmpeg / ffprobe not found.")
        print("  macOS:  brew install ffmpeg")
        print("  Ubuntu: sudo apt-get install ffmpeg")
        sys.exit(1)


def run(cmd: list, label: str = "") -> subprocess.CompletedProcess:
    """Run an ffmpeg command; exit with the exact command on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\nERROR{' in ' + label if label else ''}: FFmpeg command failed:")
        print("  " + " ".join(cmd))
        print(result.stderr[-2000:])
        sys.exit(1)
    return result


def get_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def format_timestamp(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def split_title(title: str, max_per_line: int = 20) -> tuple[str, str]:
    """Split title at the word boundary closest to the middle."""
    words = title.split()
    if len(title) <= max_per_line:
        return title, ""
    mid = len(title) // 2
    best_pos = 0
    closest = len(title)
    pos = 0
    for i, w in enumerate(words):
        if i > 0:
            pos += 1  # space
        if abs(pos - mid) < closest:
            closest = abs(pos - mid)
            best_pos = i
        pos += len(w)
    line1 = " ".join(words[:best_pos]) if best_pos > 0 else words[0]
    line2 = " ".join(words[best_pos:]) if best_pos > 0 else " ".join(words[1:])
    return line1[:max_per_line*2], line2[:max_per_line*2]


def timestamp_to_run_id(ts: str) -> str:
    """Convert '2026-05-05T10:42:24.594002' → '20260505_104224'."""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y%m%d_%H%M%S")
    except ValueError:
        return ""


# ─── step 1 & 2: read log + find files ────────────────────────────────────────

def _build_story_id_index() -> dict[str, Path]:
    """Scan all output/{run_id}/story.json files and return {story_id: final.mp4 path}."""
    index = {}
    output_root = Path("output")
    if not output_root.exists():
        return index
    for run_dir in sorted(output_root.iterdir()):
        story_json = run_dir / "story.json"
        final_mp4 = run_dir / "final.mp4"
        if not story_json.exists() or not final_mp4.exists():
            continue
        try:
            data = json.loads(story_json.read_text())
            sid = data.get("id")
            if sid:
                index[sid] = final_mp4
        except (json.JSONDecodeError, OSError):
            pass
    return index


def load_candidates(top_n: int) -> list[dict]:
    if not LOG_FILE.exists():
        print(f"ERROR: {LOG_FILE} not found.")
        sys.exit(1)

    story_index = _build_story_id_index()

    rows = []
    with open(LOG_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            story_id = row.get("story_id", "").strip()
            video_path = story_index.get(story_id)
            if not video_path:
                continue

            # Retention: use column if present and non-zero
            raw_ret = row.get("average_percentage_viewed", "").strip()
            if raw_ret and float(raw_ret) > 0:
                retention = float(raw_ret)
            else:
                retention = None

            rows.append({
                "story_id": story_id,
                "story_title": row.get("story_title", "Untitled").strip('"'),
                "youtube_url": row.get("youtube_url", ""),
                "video_duration": float(row.get("video_duration", 0) or 0),
                "retention": retention,
                "path": video_path,
                "genre": _infer_genre(row.get("story_title", "")),
            })

    # Sort: rows with real retention first (desc), then by video_duration desc
    rows.sort(key=lambda r: (r["retention"] is not None, r["retention"] or 0, r["video_duration"]), reverse=True)

    print(f"Found {len(rows)} eligible videos in upload log")

    selected = rows[:top_n]
    if len(selected) < 3:
        missing = [str(Path("output") / r["run_id"] / "final.mp4") for r in rows]
        print(f"ERROR: Need at least 3 valid videos, found {len(selected)}.")
        if missing:
            print("  Files checked:")
            for p in missing:
                print(f"    {p}")
        sys.exit(1)

    for i, v in enumerate(selected, 1):
        ret_str = f"{v['retention']}% retention" if v["retention"] else f"{v['video_duration']:.0f}s"
        print(f"  #{i} — {v['story_title']} ({ret_str}) — {v['path']}")

    return selected


def _infer_genre(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["will", "estate", "inherit", "attorney", "brother", "sister", "family", "grandp"]):
        return "family"
    if any(w in t for w in ["boss", "work", "fired", "patent", "partner", "office", "career"]):
        return "workplace"
    return "mixed"


# ─── step 3: normalize ────────────────────────────────────────────────────────

def normalize_clips(videos: list[dict]) -> list[Path]:
    print("\n[3/9] Normalizing clips...")
    normalized = []
    for i, v in enumerate(videos, 1):
        out = TMP_DIR / f"normalized_{i}.mp4"
        print(f"  Normalizing clip {i}/{len(videos)}...")
        run([
            "ffmpeg", "-y", "-i", str(v["path"]),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-r", "30",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-ar", "44100", "-ac", "2",
            "-pix_fmt", "yuv420p",
            str(out)
        ], f"normalize clip {i}")
        normalized.append(out)
    return normalized


# ─── step 4: title cards ──────────────────────────────────────────────────────

def make_title_cards(videos: list[dict]) -> list[Path]:
    print("\n[4/9] Creating title cards...")
    total = len(videos)
    cards = []
    for i, v in enumerate(videos, 1):
        out = TMP_DIR / f"card_{i}.mp4"
        line1, line2 = split_title(v["story_title"])

        # Build drawtext filter — skip empty line2
        drawtext_filters = [
            f"drawtext=text='{CHANNEL_NAME}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=700",
            f"drawtext=text='Story {i} of {total}':fontcolor=#888888:fontsize=36:x=(w-text_w)/2:y=860",
            f"drawtext=text='{_esc(line1)}':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=960",
        ]
        if line2:
            drawtext_filters.append(
                f"drawtext=text='{_esc(line2)}':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=1030"
            )
        drawtext_filters.append(
            "drawtext=text='Subscribe for daily stories':fontcolor=#888888:fontsize=32:x=(w-text_w)/2:y=1400"
        )

        vf = ",".join(drawtext_filters)

        print(f"  Card {i}/{total}: {v['story_title']}")
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=black:s=1080x1920:d=3",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-ar", "44100", "-ac", "2",
            "-pix_fmt", "yuv420p",
            str(out)
        ], f"title card {i}")
        cards.append(out)
    return cards


def _esc(text: str) -> str:
    """Escape characters that break FFmpeg drawtext."""
    return text.replace("'", "’").replace(":", r"\:").replace(",", r"\,")


# ─── step 5: fades ────────────────────────────────────────────────────────────

def add_fades(normalized: list[Path]) -> list[Path]:
    print("\n[5/9] Adding fade transitions...")
    faded = []
    for i, clip in enumerate(normalized, 1):
        out = TMP_DIR / f"faded_{i}.mp4"
        duration = get_duration(clip)
        fade_out_start = max(0.0, duration - 0.5)
        print(f"  Fading clip {i}/{len(normalized)} ({duration:.1f}s)...")
        run([
            "ffmpeg", "-y", "-i", str(clip),
            "-vf", f"fade=t=in:st=0:d=0.5,fade=t=out:st={fade_out_start:.3f}:d=0.5",
            "-af", f"afade=t=in:st=0:d=0.5,afade=t=out:st={fade_out_start:.3f}:d=0.5",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-ar", "44100", "-ac", "2",
            "-pix_fmt", "yuv420p",
            str(out)
        ], f"fade clip {i}")
        faded.append(out)
    return faded


# ─── step 6: concat list ──────────────────────────────────────────────────────

def build_concat_list(cards: list[Path], faded: list[Path]) -> Path:
    print("\n[6/9] Building concat list...")
    concat_file = TMP_DIR / "concat_list.txt"
    lines = []
    for card, clip in zip(cards, faded):
        lines.append(f"file '{card.resolve()}'")
        lines.append(f"file '{clip.resolve()}'")
    concat_file.write_text("\n".join(lines))
    print(f"  {len(lines)} segments listed")
    return concat_file


# ─── step 7: concatenate ──────────────────────────────────────────────────────

def concatenate(concat_file: Path) -> Path:
    print("\n[7/9] Concatenating...")
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-b:v", "4M",
        "-movflags", "+faststart",
        str(FINAL_OUTPUT)
    ], "concatenate")
    print(f"  Written: {FINAL_OUTPUT}")
    return FINAL_OUTPUT


# ─── step 8: metadata ─────────────────────────────────────────────────────────

def generate_metadata(videos: list[dict], faded_clips: list[Path]):
    print("\n[8/9] Generating upload metadata...")

    # Title based on dominant genre
    genres = [v["genre"] for v in videos]
    dominant = max(set(genres), key=genres.count)
    n = len(videos)
    if dominant == "family":
        title = f"{n} Family Betrayal Stories That Will Leave You Speechless"
    elif dominant == "workplace":
        title = f"{n} Workplace Revenge Stories That Ended Careers"
    else:
        title = f"{n} True Stories of Betrayal and Justice"

    # Timestamps: card (3s) + clip duration per story
    timestamps = []
    cursor = 0.0
    for i, (v, clip) in enumerate(zip(videos, faded_clips)):
        timestamps.append((cursor, v["story_title"]))
        card_dur = 3.0
        clip_dur = get_duration(clip)
        cursor += card_dur + clip_dur

    ts_lines = "\n".join(
        f"{format_timestamp(t)} - {title_}" for t, title_ in timestamps
    )

    story_lines = "\n".join(
        f"Story {i+1}: {v['story_title']}"
        + (f" ({v['retention']}% audience retention)" if v["retention"] else "")
        for i, v in enumerate(videos)
    )

    total_duration = get_duration(FINAL_OUTPUT)
    total_mins = int(total_duration) // 60
    total_secs = int(total_duration) % 60

    description = f"""\
Five of our highest-rated stories in one video.

{story_lines}

Timestamps:
{ts_lines}

New stories every day. Subscribe so you never miss one."""

    metadata = f"""\
=== COMPILATION UPLOAD METADATA ===

TITLE:
{title}

DESCRIPTION:
{description}

TAGS:
family betrayal, inheritance drama, revenge stories, true stories, family drama,
justice served, workplace revenge, satisfying stories, shorts compilation
"""

    METADATA_FILE.write_text(metadata)
    print(f"  Saved: {METADATA_FILE}")
    return total_mins, total_secs, total_duration


# ─── step 9: summary ──────────────────────────────────────────────────────────

def print_summary(videos: list[dict], faded_clips: list[Path], total_mins: int, total_secs: int):
    size_mb = FINAL_OUTPUT.stat().st_size / (1024 * 1024)
    print("\n" + "="*39)
    print("COMPILATION COMPLETE")
    print("="*39)
    print(f"Output: {FINAL_OUTPUT}")
    print(f"Total runtime: {total_mins} minutes {total_secs} seconds")
    print(f"File size: {size_mb:.1f} MB")
    print("\nStories included:")
    for i, (v, clip) in enumerate(zip(videos, faded_clips), 1):
        dur = get_duration(clip)
        ret_str = f"{v['retention']}% retention" if v["retention"] else "no retention data"
        print(f"  {i}. {v['story_title']} — {ret_str} — {dur:.0f}s")
    print(f"\nUpload metadata saved to:\n{METADATA_FILE}")
    print("\nNEXT STEP: Upload manually to YouTube as a")
    print("regular video (not a Short). Use the title and")
    print("description from metadata.txt.")
    print("="*39)


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Create YouTube compilation from top Shorts")
    parser.add_argument("--top", type=int, default=5, help="Number of videos to include (default 5)")
    parser.add_argument("--dry-run", action="store_true", help="Show which videos would be included, then exit")
    args = parser.parse_args()

    check_ffmpeg()

    print("\n[1/9] Reading upload log...")
    print("[2/9] Finding video files...")
    videos = load_candidates(args.top)

    if args.dry_run:
        print("\nDRY RUN — no files created.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    try:
        normalized = normalize_clips(videos)
        cards = make_title_cards(videos)
        faded = add_fades(normalized)
        concat_file = build_concat_list(cards, faded)

        print("\n[7/9] Concatenating...")
        concatenate(concat_file)

        total_mins, total_secs, _ = generate_metadata(videos, faded)
        print_summary(videos, faded, total_mins, total_secs)

        # Clean up tmp on success
        shutil.rmtree(TMP_DIR)

    except SystemExit:
        print("\nTMP files kept for debugging:", TMP_DIR)
        raise


if __name__ == "__main__":
    main()
