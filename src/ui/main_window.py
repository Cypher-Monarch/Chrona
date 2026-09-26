"""Chrona Qt user interface."""

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
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

from audio.engine import TTSEngine
from audio.exporters import save_as_mp3
from audio.piper import Piper, PiperVoice
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

        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)

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
            text = read_document(file_path)
            self.log("✅ File loaded. Processing...")

            if self.speak_radio.isChecked():
                self.speak(text)
                self.log("✅ Spoken aloud successfully!")

            elif self.mp3_radio.isChecked():
                file_name = Path(file_path).stem
                output_path = save_as_mp3(
                    self.tts,
                    text,
                    file_name,
                )

                self.log(f"Saved MP3: {output_path}")

            else:
                self.speak(text)

                file_name = Path(file_path).stem
                output_path = save_as_mp3(
                    self.tts,
                    text,
                    file_name,
                )

                self.log(f"✅ Spoken and MP3 saved at:\n{output_path}")

        except Exception as exc:
            self.log(f"❌ Error: {exc}")

    def speak(self, text: str) -> None:
        """Render text with Piper and play the resulting audio."""
        output_path = Path("/tmp/chrona-speech.wav")

        self.tts.save_to_wav(
            text,
            output_path,
        )

        self.player.setSource(QUrl.fromLocalFile(str(output_path)))
        self.player.play()
