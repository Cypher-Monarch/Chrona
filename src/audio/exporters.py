"""Audio export functions."""

import subprocess
from pathlib import Path

from audio.engine import AudioChunk
from constants import DOCUMENTS_FOLDER


class MP3Exporter:
    """Stream PCM audio chunks into FFmpeg and produce an MP3 file."""

    def __init__(self, file_name: str):
        DOCUMENTS_FOLDER.mkdir(parents=True, exist_ok=True)

        self.output_path = DOCUMENTS_FOLDER / f"{file_name}.mp3"
        self.process: subprocess.Popen[bytes] | None = None
        self.started = False
        self.finished = False

    def start(self, chunk: AudioChunk) -> None:
        """Start FFmpeg using the format of the first audio chunk."""
        if self.started:
            return

        self.process = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-f",
                "s16le",
                "-ar",
                str(chunk.sample_rate),
                "-ac",
                str(chunk.channels),
                "-i",
                "pipe:0",
                "-codec:a",
                "libmp3lame",
                str(self.output_path),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        self.started = True

    def write(self, chunk: AudioChunk) -> None:
        """Write a PCM chunk to FFmpeg."""
        if not self.started:
            self.start(chunk)

        if self.process is None or self.process.stdin is None:
            raise RuntimeError("FFmpeg input is unavailable.")

        self.process.stdin.write(chunk.data)

    def finish(self) -> Path:
        """Finish FFmpeg and return the generated MP3 path."""
        if self.finished:
            return self.output_path

        if self.process is None:
            raise RuntimeError("No audio was produced.")

        if self.process.stdin is not None:
            self.process.stdin.close()

        return_code = self.process.wait()

        if return_code != 0:
            error = ""

            if self.process.stderr is not None:
                error = (
                    self.process.stderr.read().decode("utf-8", errors="replace").strip()
                )

            raise RuntimeError(f"FFmpeg exited with status {return_code}: {error}")

        self.finished = True
        return self.output_path

    def abort(self) -> None:
        """Terminate FFmpeg if export is still running."""
        if self.process is not None and self.process.poll() is None:
            self.process.kill()
            self.process.wait()
