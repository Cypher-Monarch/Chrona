"""Text-to-speech and audio export services."""

import os
from pathlib import Path
from typing import Any, cast

import pyttsx3
from pydub import AudioSegment

from .config import DOCUMENTS_FOLDER


class TTSService:
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

    def save_as_mp3(
        self,
        text: str,
        file_name: str,
        rate: int,
        volume: float,
        voice_id: str,
    ) -> Path:
        DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)

        output_path = DOCUMENTS_FOLDER / f"{file_name}.mp3"
        temp_wav = DOCUMENTS_FOLDER / "temp.wav"

        self._configure(rate, volume, voice_id)
        self.engine.save_to_file(text, str(temp_wav))
        self.engine.runAndWait()

        audio = AudioSegment.from_wav(temp_wav)
        audio.export(output_path, format="mp3")
        os.remove(temp_wav)

        return output_path

    def _configure(self, rate: int, volume: float, voice_id: str) -> None:
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.engine.setProperty("voice", voice_id)
