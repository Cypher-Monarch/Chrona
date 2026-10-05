from queue import Queue

from PySide6.QtCore import QObject, Signal, Slot

from audio.engine import AudioChunk, TTSEngine, silence_chunk
from constants import MAX_SYNTHESIS_CHARS, PARAGRAPH_PAUSE_SECONDS
from documents.normalizer import split_paragraphs, split_synthesis_chunks


class AudioWorker(QObject):
    # Generate audio and place it into a bounded PCM queue.

    finished = Signal()
    cancelled = Signal()
    error = Signal(str)

    def __init__(
        self,
        engine: TTSEngine,
        text: str,
        audio_queue: Queue[AudioChunk],
    ):
        super().__init__()
        self.engine = engine
        self.text = text
        self.audio_queue = audio_queue
        self.cancel_requested = False

    def cancel(self) -> None:
        self.cancel_requested = True
        self.engine.cancel()

    @Slot()
    def run(self) -> None:
        try:
            paragraphs = split_paragraphs(self.text)

            for index, paragraph in enumerate(paragraphs):
                if len(paragraph) <= MAX_SYNTHESIS_CHARS:
                    synthesis_chunks = [paragraph]
                else:
                    synthesis_chunks = split_synthesis_chunks(paragraph)

                for synthesis_chunk in synthesis_chunks:
                    for audio_chunk in self.engine.synthesize(synthesis_chunk):
                        self.audio_queue.put(audio_chunk)

                if index < len(paragraphs) - 1:
                    self.audio_queue.put(
                        silence_chunk(
                            self.engine.voice.sample_rate,
                            self.engine.voice.channels,
                            PARAGRAPH_PAUSE_SECONDS,
                        )
                    )

            if self.cancel_requested:
                self.cancelled.emit()
                return

            self.finished.emit()

        except Exception as exc:
            if self.cancel_requested:
                self.cancelled.emit()
            else:
                self.error.emit(str(exc))
