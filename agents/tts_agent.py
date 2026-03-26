"""
Agent 2: Text-to-Speech
Uses edge-tts (free Microsoft Azure neural voices) to generate narration audio.
Completely free, no API key needed, high quality voices.
"""

import asyncio
import re
from pathlib import Path
from config import Config


class TTSAgent:
    def __init__(self, config: Config):
        self.config = config

    async def synthesize(self, text: str, output_path: Path) -> tuple[Path, list[dict]]:
        """Convert text to speech. Returns (audio_path, word_timings).

        Uses --write-subtitles to get phrase-level timing from edge-tts,
        then distributes individual words within each phrase proportionally.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        vtt_path = output_path.with_suffix(".vtt")

        cmd = [
            "edge-tts",
            "--voice", self.config.tts_voice,
            "--rate", self.config.tts_rate,
            "--text", text,
            "--write-media", str(output_path),
            "--write-subtitles", str(vtt_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {stderr.decode()}")

        duration = await self._get_audio_duration(output_path)
        print(f"      Voice: {self.config.tts_voice} | Duration: {duration:.1f}s")

        phrases = self._parse_vtt(vtt_path)
        word_timings = self._interpolate_words(phrases)
        return output_path, word_timings

    def _parse_vtt(self, vtt_path: Path) -> list[dict]:
        """Parse VTT into phrase-level timing dicts."""
        phrases = []
        content = vtt_path.read_text(encoding="utf-8")
        for block in content.strip().split("\n\n"):
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            ts_line = next((l for l in lines if "-->" in l), None)
            if ts_line is None:
                continue
            ts_idx = lines.index(ts_line)
            parts = ts_line.split("-->")
            start = self._vtt_time_to_seconds(parts[0].strip())
            end = self._vtt_time_to_seconds(parts[1].strip())
            phrase_text = " ".join(lines[ts_idx + 1:]).strip()
            # Strip punctuation for cleaner word-level display
            phrase_text = re.sub(r"[^\w\s''-]", "", phrase_text).strip()
            if phrase_text:
                phrases.append({"text": phrase_text, "start": start, "end": end})
        return phrases

    @staticmethod
    def _interpolate_words(phrases: list[dict]) -> list[dict]:
        """Distribute words equally within each phrase for readable subtitles."""
        word_timings = []
        for phrase in phrases:
            words = phrase["text"].split()
            if not words:
                continue
            phrase_duration = phrase["end"] - phrase["start"]
            word_duration = phrase_duration / len(words)

            current = phrase["start"]
            for word in words:
                word_timings.append({
                    "text": word,
                    "start": round(current, 3),
                    "end": round(current + word_duration, 3),
                })
                current += word_duration

        return word_timings

    @staticmethod
    def _vtt_time_to_seconds(t: str) -> float:
        t = t.split()[0].replace(",", ".")  # normalize comma decimals
        parts = t.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        return int(parts[0]) * 60 + float(parts[1])

    async def get_duration(self, audio_path: Path) -> float:
        return await self._get_audio_duration(audio_path)

    async def _get_audio_duration(self, audio_path: Path) -> float:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 55.0

    @staticmethod
    def list_voices():
        """Print available English voices. Run this to pick a voice."""
        import subprocess
        result = subprocess.run(
            ["edge-tts", "--list-voices"],
            capture_output=True, text=True
        )
        voices = [
            line for line in result.stdout.splitlines()
            if "en-US" in line or "en-GB" in line or "en-AU" in line
        ]
        print("\nAvailable English voices:")
        for v in voices:
            print(f"  {v}")


# ── Good voice recommendations ────────────────────────────────────────────────
# Male narrators (deep, dramatic):
#   en-US-ChristopherNeural   ← great for serious drama
#   en-US-GuyNeural           ← friendly narrator
#   en-GB-RyanNeural          ← British authority
#
# Female narrators:
#   en-US-JennyNeural         ← warm, relatable
#   en-US-AriaNeural          ← expressive
#   en-GB-SoniaNeural         ← sophisticated
#
# Run: edge-tts --list-voices | grep en-  to see all options
