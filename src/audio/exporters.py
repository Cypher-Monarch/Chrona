import os
from pathlib import Path

from pydub import AudioSegment

from audio.engine import TTSEngine
from constants import DOCUMENTS_FOLDER


def save_as_mp3(
    engine: TTSEngine,
    text: str,
    file_name: str,
) -> Path:
    """Render text with Piper and save it as an MP3."""
    DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)

    output_path = DOCUMENTS_FOLDER / f"{file_name}.mp3"
    temp_wav = DOCUMENTS_FOLDER / "temp.wav"

    engine.save_to_wav(
        text,
        temp_wav,
    )

    audio = AudioSegment.from_wav(temp_wav)
    audio.export(output_path, format="mp3")

    os.remove(temp_wav)

    return output_path
