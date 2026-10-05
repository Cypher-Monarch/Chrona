"""Chrona Qt user interface."""

from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSlider,
    QWidget,
)

from audio.engine import TTSEngine
from audio.piper import Piper, PiperVoice
from documents.normalizer import normalize_text
from documents.reader import read_document
from ui.audio_controller import AudioController
from ui.layout import build_layout
from ui.styles import ADVANCED_HINT_STYLE, APP_STYLE, STATUS_STYLE
from ui.widgets import build_widgets
from ui.window import build_window
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

        build_window(self)
        build_widgets(self)
        build_layout(self)

        self.audio_controller = AudioController(
            self.tts,
            self.log,
            lambda: self.speak_radio.isChecked() or self.both_radio.isChecked(),
            lambda: self.mp3_radio.isChecked() or self.both_radio.isChecked(),
            self,
        )

        self._apply_styles()
        check_for_updates(self)

    def _apply_styles(self) -> None:
        self.status_label.setStyleSheet(STATUS_STYLE)

        self.advanced_hint.setStyleSheet(ADVANCED_HINT_STYLE)

        self.setStyleSheet(APP_STYLE)

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
            text = normalize_text(read_document(file_path))
            self.audio_controller.set_output_file_name(Path(file_path).stem)

            self.log("✅ File loaded. Processing...")
            self.audio_controller.render_audio(text)

        except Exception as exc:
            self.log(f"❌ Error: {exc}")

    status_label: QLabel
    label: QLabel
    voice_dropdown: QComboBox
    slider_label: QLabel
    speed_slider: QSlider

    speak_radio: QRadioButton
    mp3_radio: QRadioButton
    both_radio: QRadioButton
    mode_group: QButtonGroup

    button: QPushButton

    advanced_options_container: QWidget
    advanced_hint: QLabel
