"""Text-to-speech and audio export services."""

from pathlib import Path
from typing import Any, cast

import pyttsx3


class TTSEngine:
    """Owns the TTS engine and exposes Chrona's audio operations."""

    def __init__(self):
        self.engine = pyttsx3.init()

    @property
    def voices(self) -> list[Any]:
        return cast(list[Any], self.engine.getProperty("voices"))

    def speak(self, text: str, rate: int, volume: float, voice_id: str) -> None:
        self._configure(rate, volume, voice_id)
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_wav(
        self,
        text: str,
        output_path: Path,
        rate: int,
        volume: float,
        voice_id: str,
    ) -> None:
        self._configure(rate, volume, voice_id)
        self.engine.save_to_file(text, str(output_path))
        self.engine.runAndWait()

    def _configure(self, rate: int, volume: float, voice_id: str) -> None:
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.engine.setProperty("voice", voice_id)
