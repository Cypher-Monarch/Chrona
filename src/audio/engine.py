import subprocess
from collections.abc import Iterator
from dataclasses import dataclass

from audio.piper import PiperVoice


@dataclass(frozen=True)
class AudioChunk:
    """A chunk of raw PCM audio."""

    data: bytes
    sample_rate: int
    channels: int


def silence_chunk(sample_rate: int, channels: int, duration: float) -> AudioChunk:
    """Create a silent PCM audio chunk."""
    sample_count = int(sample_rate * duration)
    byte_count = sample_count * channels * 2
    return AudioChunk(
        data=b"\x00" * byte_count,
        sample_rate=sample_rate,
        channels=channels,
    )


class TTSEngine:
    """Provides text-to-speech through Piper."""

    def __init__(self, piper_path: str, voice: PiperVoice):
        self.piper_path = piper_path
        self.voice = voice

    def synthesize(self, text: str) -> Iterator[AudioChunk]:
        """Run Piper and yield raw PCM audio chunks."""
        process = subprocess.Popen(
            [
                self.piper_path,
                "-m",
                str(self.voice.model_path),
                "--output_raw",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None

        try:
            process.stdin.write(text.encode("utf-8"))
            process.stdin.close()

            while True:
                data = process.stdout.read(4096)

                if not data:
                    break

                yield AudioChunk(
                    data=data,
                    sample_rate=self.voice.sample_rate,
                    channels=self.voice.channels,
                )

            return_code = process.wait()

            if return_code != 0:
                error = (
                    process.stderr.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                    .strip()
                )

                raise RuntimeError(f"Piper exited with status {return_code}: {error}")

        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
