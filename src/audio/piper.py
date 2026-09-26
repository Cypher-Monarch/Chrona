"""Piper installation and voice discovery."""

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
        search_root: Path,
    ) -> PiperVoice | None:
        """Parse voice metadata from a Piper model path."""
        try:
            parts = model_path.relative_to(search_root).parts
        except ValueError:
            return None

        if len(parts) < 4:
            return None

        _, language, speaker, quality = parts[:4]

        return PiperVoice(
            name=f"{speaker.title()} ({language})",
            language=language,
            speaker=speaker,
            quality=quality,
            model_path=model_path,
        )
