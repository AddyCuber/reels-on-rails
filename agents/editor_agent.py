"""
Agent 4: Video Editor
Uses FFmpeg to:
- Trim/concat B-roll clips to match audio length
- Stack two clips vertically (split-screen 1080x960 each = 1080x1920 total)
- Burn word-by-word subtitles using ASS format (centered, Impact font)
- Export in 1080x1920 (9:16) for Shorts/Reels
"""

import asyncio
import itertools
import shutil
from pathlib import Path
from config import Config


class EditorAgent:
    def __init__(self, config: Config, personality=None):
        self.config = config
        self.personality = personality

    async def compile(
        self,
        audio_path: Path,
        video_clips: list[Path],
        subtitles: list[dict],
        output_path: Path,
        card_text: str = "",
    ) -> Path:
        """Full pipeline: prepare → stack pairs → concat → add audio + subtitles."""
        output_path = Path(output_path)
        tmp_dir = output_path.parent / "tmp"
        tmp_dir.mkdir(exist_ok=True)

        layout = self.personality.layout if self.personality else "split_screen"

        # Step 1: Get audio duration
        audio_duration = await self._get_duration(audio_path)
        print(f"      Audio duration: {audio_duration:.1f}s | Layout: {layout}")

        if layout == "single_clip":
            # Full-frame clips (1080x1920) — no split-screen
            full_clips = await self._prepare_clips_fullframe(video_clips, tmp_dir)
            concat_path = tmp_dir / "concat.mp4"
            await self._concat_clips(full_clips, concat_path, audio_duration)
        else:
            # Step 2: Scale each clip to half-height (1080x960)
            half_clips = await self._prepare_clips(video_clips, tmp_dir)

            # Step 3: Pair clips and vstack into 1080x1920 frames
            stacked_clips = await self._stack_clip_pairs(half_clips, tmp_dir)

            # Step 4: Concatenate stacked frames to fill audio duration
            concat_path = tmp_dir / "concat.mp4"
            await self._concat_clips(stacked_clips, concat_path, audio_duration)

        # Step 5: Mix audio + burn subtitles → final output
        # First add audio and subtitles to a temp file
        temp_audio_sub = tmp_dir / "temp_audio_sub.mp4"
        await self._add_audio_and_subtitles(
            video_path=concat_path,
            audio_path=audio_path,
            subtitles=subtitles,
            output_path=temp_audio_sub
        )

        # Step 6: Generate and overlay Reddit hook card
        if card_text:
            display_text = card_text
        else:
            display_text = " ".join([c["text"] for c in subtitles])[:200]
        card_png = tmp_dir / "hook_card.png"
        await self._generate_hook_card(display_text, card_png)
        
        await self._overlay_hook_card(temp_audio_sub, card_png, output_path, subtitles)

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

    async def _prepare_clips_fullframe(self, clips: list[Path], tmp_dir: Path) -> list[Path]:
        """Scale each clip to full 1080x1920 for single_clip layout."""
        w = self.config.video_width
        h = self.config.video_height

        async def prep_one(i: int, clip: Path) -> Path:
            out = tmp_dir / f"full_{i:03d}.mp4"
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

        fade_dur = 0.5
        file_list = []
        dur_list = []
        total = 0.0
        safety = 0
        for path, dur in itertools.cycle(clip_durations):
            if total >= target_duration + 2 or safety >= 100:
                break
            file_list.append(path)
            dur_list.append(dur)
            if safety == 0:
                total += dur
            else:
                total += (dur - fade_dur)
            safety += 1

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
        """Write subtitle chunks as an ASS file with bottom-center alignment."""
        w = self.config.video_width
        h = self.config.video_height

        # Use personality subtitle color if available, else fall back to config style
        if self.personality:
            primary = self.personality.ass_primary_color()
            outline_color = "&H00000000"
        else:
            sub_style = getattr(self.config, "subtitle_style", {})
            primary = sub_style.get("color", "&H00FFFFFF")
            outline_color = sub_style.get("outline", "&H00000000")

        style = (
            f"Style: Default,"
            f"{self.config.subtitle_font},"
            f"{self.config.subtitle_fontsize},"
            f"{primary},"    # primary color
            f"&H000000FF,"   # secondary: black
            f"{outline_color},"   # outline color
            f"&H80000000,"   # back: semi-transparent black
            f"-1,"           # bold
            f"0,0,0,"        # italic, underline, strikeout
            f"100,100,0,0,"  # scaleX, scaleY, spacing, angle
            f"1,"            # border style (outline+shadow)
            f"{self.config.subtitle_outline_width},"
            f"2,"            # shadow depth
            f"2,"            # alignment: bottom-center (numpad 2)
            f"10,10,80,1"    # marginL, marginR, marginV, encoding
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

    async def _generate_hook_card(self, text: str, output_path: Path):
        """Generate a Reddit-style hook card using Pillow."""
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import random
        
        text = text[:280]
        if len(text) == 280:
            text += "..."

        def _load_font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
            candidates = (
                ["Arial Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
                if bold else
                ["Arial.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
            )
            for path in candidates:
                try:
                    return ImageFont.truetype(path, size)
                except OSError:
                    pass
            return ImageFont.load_default(size=size)

        font_body     = _load_font(bold=True,  size=42)
        font_top_15   = _load_font(bold=True,  size=15)
        font_top_14   = _load_font(bold=False, size=14)
        font_bold_16  = _load_font(bold=True,  size=16)
        font_normal_16 = _load_font(bold=False, size=16)
        font_emoji_16  = font_normal_16

        width = 940
        pad_x = 28
        max_text_width = width - (pad_x * 2)
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            w = font_body.getlength(test_line) if hasattr(font_body, 'getlength') else len(test_line)*20
            if w <= max_text_width:
                current_line.append(word)
            else:
                if not current_line:
                    lines.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        if len(lines) > 5:
            lines = lines[:5]
            lines[-1] = lines[-1][:-3] + "..."
            
        line_height = int(42 * 1.35)
        body_height = len(lines) * line_height
        
        top_row_height = 52
        divider_h = 1
        body_y = top_row_height + divider_h + 20
        action_row_y = body_y + body_height + 20
        pill_height = 12 + 16 + 12
        height = action_row_y + pill_height + 28
        
        shadow_blur = 16
        shadow_offset_y = 4
        pad = shadow_blur + 10
        
        img = Image.new("RGBA", (width + pad*2, height + pad*2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        shadow = Image.new("RGBA", (width, height), (0, 0, 0, int(0.15*255)))
        shadow_img = Image.new("RGBA", (width + pad*2, height + pad*2), (0, 0, 0, 0))
        shadow_img.paste(shadow, (pad, pad + shadow_offset_y))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur))
        img.alpha_composite(shadow_img)

        card_rect = [pad, pad, pad + width, pad + height]
        draw.rounded_rectangle(card_rect, radius=20, fill="#FFFFFF", outline="#EDEFF1", width=1)

        text_y = pad + (top_row_height - 15) // 2
        curr_x = pad + pad_x
        
        draw.text((curr_x, text_y), "r/TrueOffMyChest", font=font_top_15, fill="#FF4500")
        curr_x += (font_top_15.getlength("r/TrueOffMyChest") if hasattr(font_top_15, 'getlength') else 120) + 8
        
        draw.text((curr_x, text_y), "•", font=font_top_14, fill="#878A8C")
        curr_x += (font_top_14.getlength("•") if hasattr(font_top_14, 'getlength') else 10) + 8
        
        user_str = f"u/throwaway_{random.randint(1000, 9999)}"
        draw.text((curr_x, text_y), user_str, font=font_top_14, fill="#878A8C")
        curr_x += (font_top_14.getlength(user_str) if hasattr(font_top_14, 'getlength') else 100) + 8
        
        draw.text((curr_x, text_y), "•", font=font_top_14, fill="#878A8C")
        curr_x += (font_top_14.getlength("•") if hasattr(font_top_14, 'getlength') else 10) + 8
        
        time_str = random.choice(["2h ago", "4h ago", "6h ago"])
        draw.text((curr_x, text_y), f"Posted {time_str}", font=font_top_14, fill="#878A8C")

        div_y = pad + top_row_height
        draw.line([(pad, div_y), (pad + width, div_y)], fill="#EDEFF1", width=1)

        for i, line in enumerate(lines):
            draw.text((pad + pad_x, pad + body_y + i * line_height), line, font=font_body, fill="#1A1A1B")

        curr_x = pad + pad_x
        curr_y = pad + action_row_y
        
        def get_w(t, f): return f.getlength(t) if hasattr(f, 'getlength') else len(t)*10

        upvotes = f"{random.uniform(14.2, 67.8):.1f}k"
        up_text = f"▲ {upvotes}"
        up_w = get_w(up_text, font_bold_16)
        down_text = "▼"
        down_w = get_w(down_text, font_normal_16)
        
        pill_w = 20 + up_w + 16 + down_w + 20
        draw.rounded_rectangle([curr_x, curr_y, curr_x+pill_w, curr_y+pill_height], radius=20, fill="#F6F7F8")
        draw.text((curr_x+20, curr_y+12), up_text, font=font_bold_16, fill="#FF4500")
        draw.text((curr_x+20+up_w+16, curr_y+12), down_text, font=font_normal_16, fill="#878A8C")
        
        curr_x += pill_w + 14

        def draw_pill(x, y, icon, txt, f_text, color):
            icon_w = font_emoji_16.getlength(icon) if hasattr(font_emoji_16, 'getlength') else 16
            txt_w = f_text.getlength(txt) if hasattr(f_text, 'getlength') else len(txt)*10
            pw = 20 + icon_w + 4 + txt_w + 20
            draw.rounded_rectangle([x, y, x+pw, y+pill_height], radius=20, fill="#F6F7F8")
            try:
                draw.text((x+20, y+12), icon, font=font_emoji_16, fill=color, embedded_color=True)
            except:
                draw.text((x+20, y+12), icon, font=font_emoji_16, fill=color)
            draw.text((x+20+icon_w+4, y+12), txt, font=f_text, fill=color)
            return x + pw + 14

        comments = str(random.randint(312, 1847))
        curr_x = draw_pill(curr_x, curr_y, "💬", comments, font_bold_16, "#878A8C")
        curr_x = draw_pill(curr_x, curr_y, "→", "Share", font_bold_16, "#878A8C")
        curr_x = draw_pill(curr_x, curr_y, "⭐", "Award", font_bold_16, "#878A8C")

        img.save(output_path)

    async def _overlay_hook_card(self, video_path: Path, card_path: Path, output_path: Path, subtitles: list[dict] = None):
        """Overlay the hook card onto the final video with animation."""
        w = self.config.video_width
        
        # Let's update padding since shadow_blur increased from 12 to 16, and +10 base.
        pad = 26
        img_w = 940 + 2 * pad
        x_pos = (w - img_w) / 2
        
        target_y = 160 - pad

        hook_end_time = 4.2
        if subtitles:
            char_count = 0
            for chunk in subtitles:
                char_count += len(chunk["text"]) + 1
                if char_count >= 280:
                    hook_end_time = chunk["end"]
                    break
                    
        fade_out_start = max(7.0, hook_end_time + 0.5)
        
        # Slide in 0..0.4, hold 0.4..fade_out_start, fade+slide out fade_out_start..+0.6
        y_expr = f"if(lt(t,0.4),{target_y}-420*pow(1-min(t,0.4)/0.4,2),if(lt(t,{fade_out_start}),{target_y},{target_y}-40*((t-{fade_out_start})/0.6)))"
        
        filter_complex = (
            f"[1:v]format=rgba,fade=t=in:st=0:d=0.1:alpha=1,fade=t=out:st={fade_out_start}:d=0.6:alpha=1[card_fade];"
            f"[0:v][card_fade]overlay=x={x_pos}:y='{y_expr}':eval=frame:eof_action=pass"
        )
        
        img_duration = fade_out_start + 2.0
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-loop", "1", "-t", str(img_duration), "-i", str(card_path),
            "-filter_complex", filter_complex,
            "-c:a", "copy",
            "-c:v", "libx264", "-preset", "fast",
            "-b:v", self.config.video_bitrate,
            str(output_path)
        ]
        await self._run(cmd)
