"""Piper text-to-speech engine."""

import subprocess
from pathlib import Path

from audio.piper import PiperVoice


class TTSEngine:
    """Provides text-to-speech through Piper."""

    def __init__(self, piper_path: str, voice: PiperVoice):
        self.piper_path = piper_path
        self.voice = voice

    def save_to_wav(
        self,
        text: str,
        output_path: Path,
    ) -> None:
        """Render text to a WAV file using Piper."""
        subprocess.run(
            [
                self.piper_path,
                "-m",
                str(self.voice.model_path),
                "-f",
                str(output_path),
            ],
            input=text,
            text=True,
            check=True,
        )
