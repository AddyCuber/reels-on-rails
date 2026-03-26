"""
Agent 4: Video Editor
Uses FFmpeg to:
- Trim/concat B-roll clips to match audio length
- Stack two clips vertically (split-screen 1080x960 each = 1080x1920 total)
- Burn word-by-word subtitles using ASS format (centered, Impact font)
- Export in 1080x1920 (9:16) for Shorts/Reels
"""

import asyncio
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
        """Full pipeline: prepare → stack pairs → concat → add audio + subtitles."""
        output_path = Path(output_path)
        tmp_dir = output_path.parent / "tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Step 1: Get audio duration
        audio_duration = await self._get_duration(audio_path)
        print(f"      Audio duration: {audio_duration:.1f}s")

        # Step 2: Scale each clip to half-height (1080x960)
        half_clips = await self._prepare_clips(video_clips, tmp_dir)

        # Step 3: Pair clips and vstack into 1080x1920 frames
        stacked_clips = await self._stack_clip_pairs(half_clips, tmp_dir)

        # Step 4: Concatenate stacked frames to fill audio duration
        concat_path = tmp_dir / "concat.mp4"
        await self._concat_clips(stacked_clips, concat_path, audio_duration)

        # Step 5: Mix audio + burn subtitles → final output
        await self._add_audio_and_subtitles(
            video_path=concat_path,
            audio_path=audio_path,
            subtitles=subtitles,
            output_path=output_path
        )

        print(f"      Output: {output_path} ({output_path.stat().st_size / 1e6:.1f} MB)")
        return output_path

    async def _prepare_clips(self, clips: list[Path], tmp_dir: Path) -> list[Path]:
        """Scale each clip to 1080x960 (half height for split-screen stacking)."""
        w = self.config.video_width
        h = self.config.video_height // 2  # 960

        prepared = []
        for i, clip in enumerate(clips):
            out = tmp_dir / f"prep_{i:03d}.mp4"
            # Scale to cover 1080x960, crop center
            vf = (
                f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}"
            )
            cmd = [
                "ffmpeg", "-y", "-i", str(clip),
                "-vf", vf,
                "-r", str(self.config.video_fps),
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264", "-preset", "fast",
                "-an",
                str(out)
            ]
            await self._run(cmd)
            prepared.append(out)

        return prepared

    async def _stack_clip_pairs(self, clips: list[Path], tmp_dir: Path) -> list[Path]:
        """Stack consecutive clip pairs vertically into 1080x1920 frames."""
        if len(clips) % 2 != 0:
            clips = clips + [clips[-1]]

        stacked = []
        fps = self.config.video_fps
        for i in range(0, len(clips), 2):
            top, bot = clips[i], clips[i + 1]
            out = tmp_dir / f"stack_{i // 2:03d}.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-i", str(top), "-i", str(bot),
                "-filter_complex", "[0:v][1:v]vstack=inputs=2[out]",
                "-map", "[out]",
                "-shortest",
                "-r", str(fps),
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264", "-preset", "fast",
                str(out)
            ]
            await self._run(cmd)
            stacked.append(out)

        return stacked

    async def _concat_clips(self, clips: list[Path], output: Path, target_duration: float):
        """Concat clips, looping if necessary to fill target duration."""
        concat_list = output.parent / "concat_list.txt"
        clip_durations = []
        for c in clips:
            d = await self._get_duration(c)
            clip_durations.append((c, d))

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
            "-r", str(self.config.video_fps),
            "-pix_fmt", "yuv420p",
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
        """Add audio track and burn word-by-word subtitles using ASS format."""
        ass_path = output_path.parent / "subtitles.ass"
        self._write_ass(subtitles, ass_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"ass={ass_path}",
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-b:v", self.config.video_bitrate,
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]
        await self._run(cmd)

    def _write_ass(self, chunks: list[dict], ass_path: Path):
        """Write subtitle chunks as an ASS file with center-middle alignment."""
        w = self.config.video_width
        h = self.config.video_height

        style = (
            f"Style: Default,"
            f"{self.config.subtitle_font},"
            f"{self.config.subtitle_fontsize},"
            f"&H00FFFFFF,"   # primary: white
            f"&H000000FF,"   # secondary: black
            f"&H00000000,"   # outline: black
            f"&H80000000,"   # back: semi-transparent black
            f"-1,"           # bold
            f"0,0,0,"        # italic, underline, strikeout
            f"100,100,0,0,"  # scaleX, scaleY, spacing, angle
            f"1,"            # border style (outline+shadow)
            f"{self.config.subtitle_outline_width},"
            f"2,"            # shadow depth
            f"5,"            # alignment: center-middle (numpad 5)
            f"10,10,10,1"    # marginL, marginR, marginV, encoding
        )

        header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            f"PlayResX: {w}\n"
            f"PlayResY: {h}\n"
            "Collisions: Normal\n"
            "\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"{style}\n"
            "\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        lines = [header]
        for chunk in chunks:
            start = self._seconds_to_ass_time(chunk["start"])
            end = self._seconds_to_ass_time(chunk["end"])
            text = chunk["text"].upper()
            lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        ass_path.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _seconds_to_ass_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)  # centiseconds
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

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
