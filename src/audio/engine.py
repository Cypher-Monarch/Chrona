import subprocess
from collections.abc import Iterator
from dataclasses import dataclass

from audio.piper import PiperVoice


@dataclass(frozen=True)
class AudioChunk:
    # A chunk of raw PCM audio.

    data: bytes
    sample_rate: int
    channels: int


def silence_chunk(sample_rate: int, channels: int, duration: float) -> AudioChunk:
    # Create a silent PCM audio chunk.
    sample_count = int(sample_rate * duration)
    byte_count = sample_count * channels * 2

    return AudioChunk(
        data=b"\x00" * byte_count,
        sample_rate=sample_rate,
        channels=channels,
    )


class TTSEngine:
    # Provides text-to-speech through Piper.

    def __init__(self, piper_path: str, voice: PiperVoice):
        self.piper_path = piper_path
        self.voice = voice
        self.speed = 150
        self.process: subprocess.Popen[bytes] | None = None

    def set_speed(self, speed: int) -> None:
        # Set speech speed.
        if not 80 <= speed <= 250:
            raise ValueError("Speech speed must be between 80 and 250.")

        self.speed = speed

    def cancel(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()

    def synthesize(self, text: str) -> Iterator[AudioChunk]:
        # Run Piper and yield raw PCM audio chunks.
        length_scale = 1.0 - (self.speed - 150) / 200.0

        self.process = subprocess.Popen(
            [
                self.piper_path,
                "-m",
                str(self.voice.model_path),
                "--output_raw",
                "--length_scale",
                f"{length_scale:.3f}",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert self.process.stdin is not None
        assert self.process.stdout is not None
        assert self.process.stderr is not None

        try:
            self.process.stdin.write(text.encode("utf-8"))
            self.process.stdin.close()

            while True:
                data = self.process.stdout.read(4096)

                if not data:
                    break

                yield AudioChunk(
                    data=data,
                    sample_rate=self.voice.sample_rate,
                    channels=self.voice.channels,
                )

            return_code = self.process.wait()

            if return_code != 0:
                error = (
                    self.process.stderr.read().decode("utf-8", errors="replace").strip()
                )

                raise RuntimeError(f"Piper exited with status {return_code}: {error}")

        finally:
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.kill()
                    self.process.wait()

                self.process = None
