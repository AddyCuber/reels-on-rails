"""
Agent 2: Text-to-Speech
Uses edge-tts (free Microsoft Azure neural voices) to generate narration audio.
Completely free, no API key needed, high quality voices.
"""

import asyncio
import subprocess
from pathlib import Path
from config import Config


class TTSAgent:
    def __init__(self, config: Config):
        self.config = config

    async def synthesize(self, text: str, output_path: Path) -> Path:
        """Convert text to speech using edge-tts."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # edge-tts command
        cmd = [
            "edge-tts",
            "--voice", self.config.tts_voice,
            "--rate", self.config.tts_rate,
            "--text", text,
            "--write-media", str(output_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {stderr.decode()}")

        # Get actual duration of generated audio
        duration = await self._get_audio_duration(output_path)
        print(f"      Voice: {self.config.tts_voice} | Duration: {duration:.1f}s")

        return output_path

    async def get_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds using ffprobe."""
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
            return 55.0  # fallback

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
