"""
Agent 4: Video Editor
Uses FFmpeg to:
- Trim/concat B-roll clips to match audio length
- Stack two clips vertically (split-screen 1080x960 each = 1080x1920 total)
- Burn word-by-word subtitles using ASS format (centered, Impact font)
- Export in 1080x1920 (9:16) for Shorts/Reels
"""

import asyncio
import shutil
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

        # Cleanup tmp files
        shutil.rmtree(tmp_dir, ignore_errors=True)

        print(f"      Output: {output_path} ({output_path.stat().st_size / 1e6:.1f} MB)")
        return output_path

    async def _prepare_clips(self, clips: list[Path], tmp_dir: Path) -> list[Path]:
        """Scale each clip to 1080x960 (half height for split-screen stacking)."""
        w = self.config.video_width
        h = self.config.video_height // 2  # 960

        async def prep_one(i: int, clip: Path) -> Path:
            out = tmp_dir / f"prep_{i:03d}.mp4"
            vf = (
                f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}"
            )
            cmd = [
                "ffmpeg", "-y", "-i", str(clip),
                "-vf", vf,
                "-t", str(self.config.broll_max_clip_duration),
                "-r", str(self.config.video_fps),
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264", "-preset", "fast",
                "-an",
                "-movflags", "+faststart",
                str(out)
            ]
            await self._run(cmd)
            return out

        # Process clips in parallel batches of 4
        prepared = []
        batch_size = 4
        for start in range(0, len(clips), batch_size):
            batch = [(start + j, clips[start + j]) for j in range(min(batch_size, len(clips) - start))]
            results = await asyncio.gather(*(prep_one(i, c) for i, c in batch))
            prepared.extend(results)

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
            # Trim both to the shorter clip's duration to prevent frozen frames
            dur_top = await self._get_duration(top)
            dur_bot = await self._get_duration(bot)
            min_dur = min(dur_top, dur_bot)
            cmd = [
                "ffmpeg", "-y",
                "-t", str(min_dur), "-i", str(top),
                "-t", str(min_dur), "-i", str(bot),
                "-filter_complex", "[0:v][1:v]vstack=inputs=2[out]",
                "-map", "[out]",
                "-r", str(fps),
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264", "-preset", "fast",
                str(out)
            ]
            await self._run(cmd)
            stacked.append(out)

        return stacked

    async def _concat_clips(self, clips: list[Path], output: Path, target_duration: float):
        """Concat clips with crossfade transitions, cycling to fill target duration."""
        clip_durations = []
        for c in clips:
            d = await self._get_duration(c)
            clip_durations.append((c, d))

        # Build clip list to cover target duration
        file_list = []
        dur_list = []
        total = 0.0
        idx = 0
        max_iters = 50
        while total < target_duration + 2 and max_iters > 0:
            path, dur = clip_durations[idx % len(clip_durations)]
            file_list.append(path)
            dur_list.append(dur)
            total += dur
            idx += 1
            max_iters -= 1

        if len(file_list) < 2:
            # Single clip — no crossfade needed, just copy
            concat_list = output.parent / "concat_list.txt"
            with open(concat_list, "w") as f:
                f.write(f"file '{file_list[0].resolve()}'\n")
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-t", str(target_duration + 1),
                "-c:v", "libx264", "-preset", "fast",
                str(output)
            ]
            await self._run(cmd)
            return

        # Build xfade filter chain for crossfade transitions
        fade_dur = 0.5
        inputs = []
        for p in file_list:
            inputs.extend(["-i", str(p)])

        # Chain xfade filters: [0][1]xfade → [v01], [v01][2]xfade → [v012], ...
        filters = []
        offset = dur_list[0] - fade_dur
        prev = "[0:v]"
        for i in range(1, len(file_list)):
            out_label = f"[v{i}]"
            if i == len(file_list) - 1:
                out_label = "[vout]"
            filters.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade_dur}:offset={offset:.2f}{out_label}")
            prev = out_label
            if i < len(file_list) - 1:
                offset += dur_list[i] - fade_dur

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", ";".join(filters),
            "-map", "[vout]",
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

        # Progress bar: thin red bar at bottom filling left→right over video duration
        audio_duration = await self._get_duration(audio_path)
        progress_bar = (
            f"drawbox=x=0:y=ih-8:w=iw*(t/{audio_duration:.2f}):h=8"
            f":color=red@0.85:t=fill"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"{progress_bar},ass={ass_path}",
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
            f"10,10,350,1"   # marginL, marginR, marginV, encoding
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
