"""
Agent 4: Video Editor
Uses FFmpeg to:
- Trim/concat B-roll clips to match audio length
- Add word-by-word subtitle overlays
- Apply slight zoom/Ken Burns effect
- Export in 1080x1920 (9:16) for Shorts/Reels
"""

import asyncio
import json
import subprocess
from pathlib import Path
from config import Config


class EditorAgent:
    def __init__(self, config: Config):
        self.config = config

    async def compile(
        self,
        audio_path: Path,
        video_clips: list[Path],
        subtitles: list[dict],
        output_path: Path
    ) -> Path:
        """Full pipeline: concat clips → add audio → burn subtitles → export."""
        output_path = Path(output_path)
        tmp_dir = output_path.parent / "tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Step 1: Get audio duration
        audio_duration = await self._get_duration(audio_path)
        print(f"      Audio duration: {audio_duration:.1f}s")

        # Step 2: Prepare clips (scale + crop to 9:16, trim)
        prepared_clips = await self._prepare_clips(video_clips, tmp_dir, audio_duration)

        # Step 3: Concatenate clips
        concat_path = tmp_dir / "concat.mp4"
        await self._concat_clips(prepared_clips, concat_path, audio_duration)

        # Step 4: Mix audio + subtitles → final output
        await self._add_audio_and_subtitles(
            video_path=concat_path,
            audio_path=audio_path,
            subtitles=subtitles,
            output_path=output_path
        )

        print(f"      Output: {output_path} ({output_path.stat().st_size / 1e6:.1f} MB)")
        return output_path

    async def _prepare_clips(self, clips: list[Path], tmp_dir: Path, total_needed: float) -> list[Path]:
        """Scale each clip to 1080x1920, add Ken Burns zoom."""
        prepared = []
        w, h = self.config.video_width, self.config.video_height

        for i, clip in enumerate(clips):
            out = tmp_dir / f"prep_{i:03d}.mp4"
            # Scale to cover 9:16, crop center, subtle zoom in
            vf = (
                f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h},"
                f"zoompan=z='min(zoom+0.0015,1.15)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={self.config.video_fps}"
            )
            cmd = [
                "ffmpeg", "-y", "-i", str(clip),
                "-vf", vf,
                "-c:v", "libx264", "-preset", "fast",
                "-an",  # no audio from clips
                str(out)
            ]
            await self._run(cmd)
            prepared.append(out)

        return prepared

    async def _concat_clips(self, clips: list[Path], output: Path, target_duration: float):
        """Concat clips, looping if necessary to fill target duration."""
        # Build concat list, repeating clips if needed
        concat_list = output.parent / "concat_list.txt"
        clip_durations = []
        for c in clips:
            d = await self._get_duration(c)
            clip_durations.append((c, d))

        # Fill up to target_duration + 2s buffer
        file_list = []
        total = 0.0
        while total < target_duration + 2:
            for path, dur in clip_durations:
                file_list.append(path)
                total += dur
                if total >= target_duration + 2:
                    break

        with open(concat_list, "w") as f:
            for p in file_list:
                f.write(f"file '{p.resolve()}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-t", str(target_duration + 1),
            "-c:v", "libx264", "-preset", "fast",
            str(output)
        ]
        await self._run(cmd)

    async def _add_audio_and_subtitles(
        self,
        video_path: Path,
        audio_path: Path,
        subtitles: list[dict],
        output_path: Path
    ):
        """Add audio track and burn word-by-word subtitles using drawtext filters."""
        # Build subtitle SRT file
        srt_path = output_path.parent / "subtitles.srt"
        self._write_srt(subtitles, srt_path)

        # FFmpeg command with subtitles burned in
        subtitle_style = (
            f"FontName={self.config.subtitle_font},"
            f"FontSize={self.config.subtitle_fontsize},"
            f"PrimaryColour=&H00FFFFFF,"      # white
            f"OutlineColour=&H00000000,"      # black outline
            f"Outline={self.config.subtitle_outline_width},"
            f"Alignment=2,"                   # bottom center
            f"MarginV=120"                    # above bottom edge
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"subtitles={srt_path}:force_style='{subtitle_style}'",
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-b:v", self.config.video_bitrate,
            "-shortest",
            "-movflags", "+faststart",        # web-optimized
            str(output_path)
        ]
        await self._run(cmd)

    def _write_srt(self, chunks: list[dict], srt_path: Path):
        """Write subtitle chunks as an SRT file."""
        lines = []
        for i, chunk in enumerate(chunks, 1):
            start = self._seconds_to_srt_time(chunk["start"])
            end = self._seconds_to_srt_time(chunk["end"])
            text = chunk["text"].upper()   # uppercase = more impactful
            lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        srt_path.write_text("\n".join(lines))

    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    @staticmethod
    async def _get_duration(path: Path) -> float:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 10.0

    @staticmethod
    async def _run(cmd: list[str]):
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg error:\n{stderr.decode()[-500:]}")
