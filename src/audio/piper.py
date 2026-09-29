"""Piper installation and voice discovery."""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PiperVoice:
    """Represents an installed Piper voice."""

    name: str
    language: str
    speaker: str
    quality: str
    model_path: Path
    sample_rate: int
    channels: int = 1


class Piper:
    """Discovers the Piper executable and installed voice models."""

    def __init__(self):
        self.executable = self._find_executable()

    def _find_executable(self) -> str:
        """Find the Piper executable on PATH."""
        executable = shutil.which("piper-tts") or shutil.which("piper")

        if executable is None:
            raise FileNotFoundError(
                "Piper was not found. Install Piper or configure its path."
            )

        return executable

    def find_voices(self) -> list[PiperVoice]:
        """Find installed Piper voices."""
        voices: list[PiperVoice] = []

        search_paths = [
            Path("/usr/share/piper-voices"),
            Path.home() / ".local/share/piper-voices",
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for model_path in search_path.rglob("*.onnx"):
                voice = self._parse_voice(model_path, search_path)

                if voice is not None:
                    voices.append(voice)

        return sorted(voices, key=lambda voice: voice.name)

    def _parse_voice(
        self,
        model_path: Path,
        search_path: Path,
    ) -> PiperVoice | None:
        """Parse voice metadata from a Piper model path."""
        try:
            relative_path = model_path.relative_to(search_path)
            parts = relative_path.parts

            if len(parts) < 4:
                return None

            _, language, speaker, quality = parts[:4]

            config_path = model_path.with_suffix(".onnx.json")

            with config_path.open("r", encoding="utf-8") as config_file:
                config = json.load(config_file)

            sample_rate = config["audio"]["sample_rate"]
            num_speakers = config.get("num_speakers", 1)

            return PiperVoice(
                name=f"{speaker.title()} ({language})",
                language=language,
                speaker=speaker,
                quality=quality,
                model_path=model_path,
                sample_rate=sample_rate,
                channels=1,
            )

        except (OSError, KeyError, TypeError, ValueError):
            return None
