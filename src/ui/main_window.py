"""Chrona Qt user interface."""

from pathlib import Path
from queue import Empty, Queue

from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from audio.engine import AudioChunk, TTSEngine
from audio.exporters import MP3Exporter
from audio.piper import Piper, PiperVoice
from audio.playback import AudioBuffer
from audio.worker import AudioWorker
from documents.normalizer import normalize_text
from documents.reader import read_document
from updates import check_for_updates


class TTSApp(QWidget):
    """Main Chrona application window."""

    def __init__(self, tts_engine: TTSEngine | None = None):
        super().__init__()

        self.piper = Piper()
        self.voices: list[PiperVoice] = self.piper.find_voices()

        if not self.voices:
            raise RuntimeError("No Piper voices available")

        self.voice = self.voices[0]

        self.tts = tts_engine or TTSEngine(
            self.piper.executable,
            self.voice,
        )

        self.audio_buffer = AudioBuffer()
        self.audio_sink = None
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

        self._build_window()
        self._build_widgets()
        self._build_layout()
        self._apply_styles()
        check_for_updates(self)

    def _build_window(self) -> None:
        self.setWindowTitle("Text-to-Speech & MP3 Converter")
        self.setWindowIcon(QIcon("Chrona.png"))
        self.setFixedSize(480, 420)

    def _build_widgets(self) -> None:
        self.status_label = QLabel("Status: Waiting for file...", self)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(100)

        self.label = QLabel("📄 Choose a file to convert", self)

        self.voice_dropdown = QComboBox()
        for voice in self.voices:
            self.voice_dropdown.addItem(voice.name)
        self.voice_dropdown.currentIndexChanged.connect(self.change_voice)

        self.slider_label = QLabel("🔊 Speed: 150")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(80)
        self.speed_slider.setMaximum(250)
        self.speed_slider.setValue(150)
        self.speed_slider.valueChanged.connect(self.update_speed_label)

        self.speak_radio = QRadioButton("🗣️ Speak Only")
        self.mp3_radio = QRadioButton("🎵 MP3 Only")
        self.both_radio = QRadioButton("🔊 Speak + MP3")
        self.both_radio.setChecked(True)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.speak_radio)
        self.mode_group.addButton(self.mp3_radio)
        self.mode_group.addButton(self.both_radio)

        self.button = QPushButton("Browse File", self)
        self.button.clicked.connect(self.browse_file)

        self.advanced_options_container = QWidget()
        advanced_layout = QHBoxLayout()
        advanced_layout.addWidget(self.speak_radio)
        advanced_layout.addWidget(self.mp3_radio)
        advanced_layout.addWidget(self.both_radio)
        self.advanced_options_container.setLayout(advanced_layout)
        self.advanced_options_container.setVisible(False)

        self.advanced_hint = QLabel("▶ Advanced Options")
        self.advanced_hint.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.advanced_hint.mousePressEvent = self.toggle_advanced_options

    def _build_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addSpacing(10)
        layout.addWidget(self.label)
        layout.addSpacing(5)

        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("🎤 Voice:"))
        voice_layout.addWidget(self.voice_dropdown)
        layout.addLayout(voice_layout)

        layout.addWidget(self.slider_label)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.advanced_hint)
        layout.addWidget(self.advanced_options_container)
        layout.addWidget(self.button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _apply_styles(self) -> None:
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                padding: 8px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
                color: #FFD700;
            }
        """)

        self.advanced_hint.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 12px;
                padding-right: 4px;
                text-decoration: underline;
            }
        """)

        self.setStyleSheet("""
            QWidget {
                background-color: #111111;
                color: #F0F0F0;
                font-family: Consolas, 'Courier New', monospace;
            }

            QLabel {
                color: #FFD700;
                font-size: 14px;
            }

            QPushButton {
                background-color: #FFD700;
                color: #111111;
                border: none;
                padding: 8px 12px;
                font-weight: bold;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #e6c200;
            }

            QComboBox {
                background-color: #222222;
                color: #F0F0F0;
                padding: 5px;
                border: 1px solid #444444;
                border-radius: 4px;
            }

            QSlider::groove:horizontal {
                background: #333;
                height: 4px;
            }

            QSlider::handle:horizontal {
                background: #FFD700;
                width: 12px;
                margin: -6px 0;
                border-radius: 6px;
            }
        """)

    def toggle_advanced_options(self, event=None) -> None:
        visible = self.advanced_options_container.isVisible()
        self.advanced_options_container.setVisible(not visible)
        self.advanced_hint.setText(
            "▶ Advanced Options" if visible else "▼ Advanced Options"
        )

    def log(self, message: str) -> None:
        self.status_label.setText(message)

    def update_speed_label(self, value: int) -> None:
        self.slider_label.setText(f"🔊 Speed: {value}")

    def change_voice(self, index: int) -> None:
        if not self.voices:
            return

        self.voice = self.voices[index]
        self.tts.voice = self.voice

    def browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Documents (*.txt *.docx *.pdf)",
        )

        if file_path:
            self.process_file(file_path)

    def render_audio(self, text: str) -> None:
        """Render audio in a background thread."""
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

        self.audio_thread = QThread(self)

        self.audio_worker = AudioWorker(
            self.tts,
            text,
            self.audio_queue,
        )

        self.audio_worker.moveToThread(self.audio_thread)

        self.audio_thread.started.connect(self.audio_worker.run)

        self.audio_worker.finished.connect(self.audio_render_finished)
        self.audio_worker.error.connect(self.audio_render_error)

        self.audio_worker.finished.connect(self.audio_thread.quit)
        self.audio_worker.error.connect(self.audio_thread.quit)

        self.audio_thread.finished.connect(self.audio_thread_finished)

        self.audio_thread.start()

    def audio_render_finished(self) -> None:
        """Handle completed audio synthesis."""
        self.audio_synthesis_finished = True
        self.log("✅ Audio synthesis finished.")

    def audio_render_error(self, error: str) -> None:
        """Handle background audio rendering failure."""
        self.log(f"❌ Audio rendering failed: {error}")

    def audio_thread_finished(self) -> None:
        """Clean up completed audio processing."""
        if self.audio_worker is not None:
            self.audio_worker.deleteLater()

        if self.audio_thread is not None:
            self.audio_thread.deleteLater()

        self.audio_worker = None
        self.audio_thread = None

    def audio_chunk_ready(self, chunk) -> None:
        """Buffer synthesized audio and start playback after preroll."""
        print(
            f"🔔 audio_chunk_ready(): {len(chunk.data)} bytes",
            flush=True,
        )
        if not self.audio_buffer.isOpen():
            self.audio_buffer.start()

        self.audio_buffer.append(chunk.data)

        if self.audio_sink is not None:
            return

        preroll_bytes = chunk.sample_rate * chunk.channels * 2 // 5
        buffered = self.audio_buffer.buffered_bytes()

        if buffered < preroll_bytes:
            return

        print("🔊 PREROLL REACHED", flush=True)

        audio_format = QAudioFormat()
        audio_format.setSampleRate(chunk.sample_rate)
        audio_format.setChannelCount(chunk.channels)
        audio_format.setSampleFormat(
            QAudioFormat.SampleFormat.Int16,
        )

        device = QMediaDevices.defaultAudioOutput()

        self.audio_sink = QAudioSink(audio_format, self)
        self.audio_sink.start(self.audio_buffer)

        self.audio_started = True

        self.log(f"🔊 Playback started: {device.description()}")

    def speak(self, text: str) -> None:
        """Render text with Piper and play the resulting audio."""
        self.render_audio(text)

    def drain_audio_queue(self) -> None:
        """Route synthesized audio chunks to the selected outputs."""
        max_buffer_bytes = 2 * 1024 * 1024

        while True:
            if self.speak_radio.isChecked() or self.both_radio.isChecked():
                if self.audio_buffer.buffered_bytes() >= max_buffer_bytes:
                    break

            try:
                chunk = self.audio_queue.get_nowait()
            except Empty:
                break

            if self.speak_radio.isChecked() or self.both_radio.isChecked():
                self.audio_chunk_ready(chunk)

            if self.mp3_radio.isChecked() or self.both_radio.isChecked():
                if self.mp3_exporter is None:
                    if self.output_file_name is None:
                        self.log("❌ No output filename available.")
                        return

                    self.mp3_exporter = MP3Exporter(self.output_file_name)

                self.mp3_exporter.write(chunk)

        if self.audio_synthesis_finished and self.audio_queue.empty():
            if (
                self.speak_radio.isChecked() or self.both_radio.isChecked()
            ) and not self.audio_buffer_finished:
                self.audio_buffer.finish()
                self.audio_buffer_finished = True

            if (
                self.mp3_radio.isChecked() or self.both_radio.isChecked()
            ) and not self.mp3_export_finished:
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

    def process_file(self, file_path: str) -> None:
        reply = QMessageBox.question(
            self,
            "Confirm Conversion",
            "Are you sure you want to convert this file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            self.log("⚠️ Conversion cancelled by user.")
            return

        try:
            text = normalize_text(read_document(file_path))
            self.output_file_name = Path(file_path).stem

            self.log("✅ File loaded. Processing...")
            self.render_audio(text)

        except Exception as exc:
            self.log(f"❌ Error: {exc}")
