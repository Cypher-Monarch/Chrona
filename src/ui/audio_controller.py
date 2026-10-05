# Chrona audio controller.

from collections.abc import Callable
from queue import Empty, Queue

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices

from audio.engine import AudioChunk, TTSEngine
from audio.exporters import MP3Exporter
from audio.playback import AudioBuffer
from audio.worker import AudioWorker


class AudioController(QObject):
    # Coordinate audio synthesis, playback, and MP3 export.

    def __init__(
        self,
        tts: TTSEngine,
        log: Callable[[str], None],
        speak_enabled: Callable[[], bool],
        mp3_enabled: Callable[[], bool],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.tts = tts
        self.log = log
        self.speak_enabled = speak_enabled
        self.mp3_enabled = mp3_enabled

        self.audio_buffer = AudioBuffer()
        self.audio_sink: QAudioSink | None = None
        self.audio_started = False
        self.audio_synthesis_finished = False
        self.audio_buffer_finished = False

        self.mp3_exporter: MP3Exporter | None = None
        self.mp3_export_finished = False
        self.output_file_name: str | None = None

        self.audio_queue: Queue[AudioChunk] = Queue(maxsize=32)

        self.audio_thread: QThread | None = None
        self.audio_worker: AudioWorker | None = None

        self.audio_queue_timer = QTimer(self)
        self.audio_queue_timer.setInterval(10)
        self.audio_queue_timer.timeout.connect(self.drain_audio_queue)
        self.audio_queue_timer.start()

        self.cancel_requested = False

    def set_output_file_name(self, file_name: str) -> None:
        # Set the filename used for MP3 export.
        self.output_file_name = file_name

    def render_audio(self, text: str) -> None:
        # Render audio in a background thread.
        self.cancel_requested = False
        if self.audio_thread is not None:
            self.log("⚠️ Audio processing is already running.")
            return

        if self.audio_sink is not None:
            self.audio_sink.stop()
            self.audio_sink.deleteLater()
            self.audio_sink = None

        self.audio_buffer = AudioBuffer()
        self.audio_started = False
        self.audio_synthesis_finished = False
        self.audio_buffer_finished = False
        self.mp3_exporter = None
        self.mp3_export_finished = False

        self.audio_thread = QThread(self)

        self.audio_worker = AudioWorker(
            self.tts,
            text,
            self.audio_queue,
        )

        self.audio_worker.moveToThread(self.audio_thread)

        self.audio_thread.started.connect(self.audio_worker.run)

        self.audio_worker.finished.connect(self.audio_render_finished)
        self.audio_worker.cancelled.connect(self.audio_render_cancelled)
        self.audio_worker.error.connect(self.audio_render_error)

        self.audio_worker.finished.connect(self.audio_thread.quit)
        self.audio_worker.cancelled.connect(self.audio_thread.quit)
        self.audio_worker.error.connect(self.audio_thread.quit)

        self.audio_thread.finished.connect(self.audio_thread_finished)

        self.audio_thread.start()

    def cancel(self) -> None:
        self.cancel_requested = True

        self.stop_playback()

        if self.audio_worker is not None:
            self.log("⏹️ Cancelling...")
            self.audio_worker.cancel()
        else:
            self.log("⏹️ Playback stopped.")

    def audio_render_finished(self) -> None:
        # Handle completed audio synthesis.
        self.audio_synthesis_finished = True
        self.log("✅ Audio synthesis finished.")

    def audio_render_cancelled(self) -> None:
        # Handle cancelled audio synthesis.
        self.stop_playback()

        while True:
            try:
                self.audio_queue.get_nowait()
            except Empty:
                break

        if self.mp3_exporter is not None:
            try:
                self.mp3_exporter.abort()
            except Exception:
                pass

        self.mp3_exporter = None
        self.audio_synthesis_finished = False
        self.audio_buffer_finished = False
        self.mp3_export_finished = False

        self.log("⏹️ Audio processing cancelled.")

    def stop_playback(self) -> None:
        # Stop active audio playback.
        if self.audio_sink is not None:
            self.audio_sink.reset()
            self.audio_sink.deleteLater()
            self.audio_sink = None

        self.audio_buffer = AudioBuffer()
        self.audio_started = False

        while True:
            try:
                self.audio_queue.get_nowait()
            except Empty:
                break

        if self.mp3_exporter is not None:
            try:
                self.mp3_exporter.abort()
            except Exception:
                pass

        self.mp3_exporter = None
        self.audio_synthesis_finished = False
        self.audio_buffer_finished = False
        self.mp3_export_finished = False

    def audio_render_error(self, error: str) -> None:
        # Handle background audio rendering failure.
        self.log(f"❌ Audio rendering failed: {error}")

    def audio_thread_finished(self) -> None:
        # Clean up completed audio processing.
        if self.audio_worker is not None:
            self.audio_worker.deleteLater()

        if self.audio_thread is not None:
            self.audio_thread.deleteLater()

        self.audio_worker = None
        self.audio_thread = None

    def audio_chunk_ready(self, chunk: AudioChunk) -> None:
        # Buffer synthesized audio and start playback after preroll.

        if not self.audio_buffer.isOpen():
            self.audio_buffer.start()

        self.audio_buffer.append(chunk.data)

        if self.audio_sink is not None:
            return

        preroll_bytes = chunk.sample_rate * chunk.channels * 2 // 5
        buffered = self.audio_buffer.buffered_bytes()

        if buffered < preroll_bytes:
            return

        audio_format = QAudioFormat()
        audio_format.setSampleRate(chunk.sample_rate)
        audio_format.setChannelCount(chunk.channels)
        audio_format.setSampleFormat(
            QAudioFormat.SampleFormat.Int16,
        )

        device = QMediaDevices.defaultAudioOutput()

        self.audio_sink = QAudioSink(audio_format, self)
        self.audio_sink.setBufferSize(4096)
        self.audio_sink.start(self.audio_buffer)

        self.audio_started = True

        self.log(f"🔊 Playback started: {device.description()}")

    def speak(self, text: str) -> None:
        # Render text with Piper and play the resulting audio.
        self.render_audio(text)

    def drain_audio_queue(self) -> None:
        # Route synthesized audio chunks to the selected outputs.
        if self.cancel_requested:
            return

        max_buffer_bytes = 2 * 1024 * 1024

        while True:
            if self.speak_enabled():
                if self.audio_buffer.buffered_bytes() >= max_buffer_bytes:
                    break

            try:
                chunk = self.audio_queue.get_nowait()
            except Empty:
                break

            if self.speak_enabled():
                self.audio_chunk_ready(chunk)

            if self.mp3_enabled():
                if self.mp3_exporter is None:
                    if self.output_file_name is None:
                        self.log("❌ No output filename available.")
                        return

                    self.mp3_exporter = MP3Exporter(self.output_file_name)

                self.mp3_exporter.write(chunk)

        if self.audio_synthesis_finished and self.audio_queue.empty():
            if self.speak_enabled() and not self.audio_buffer_finished:
                self.audio_buffer.finish()
                self.audio_buffer_finished = True

            if self.mp3_enabled() and not self.mp3_export_finished:
                try:
                    output_path = (
                        self.mp3_exporter.finish()
                        if self.mp3_exporter is not None
                        else None
                    )

                    self.mp3_export_finished = True

                    if output_path is not None:
                        self.log(f"✅ MP3 saved: {output_path}")

                except Exception as exc:
                    self.log(f"❌ MP3 export failed: {exc}")
