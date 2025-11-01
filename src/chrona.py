import os
import pyttsx3
import PyPDF2
import docx
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QSlider,
    QComboBox,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
)
import requests
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from pydub import AudioSegment
from pathlib import Path

# Initialize TTS engine
engine = pyttsx3.init()

VERSION = "1.0.0"


def get_documents_folder():
    return str(Path.home() / "Documents" / "Chrona")


def read_word_file(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def read_pdf_file(file_path):
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def speak(text, rate, volume, voice_id):
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.setProperty("voice", voice_id)
    engine.say(text)
    engine.runAndWait()


def save_as_mp3(text, file_name, rate, volume, voice_id):
    output_folder = get_documents_folder()
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, f"{file_name}.mp3")
    temp_wav = os.path.join(output_folder, "temp.wav")

    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.setProperty("voice", voice_id)

    engine.save_to_file(text, temp_wav)
    engine.runAndWait()

    audio = AudioSegment.from_wav(temp_wav)
    audio.export(output_path, format="mp3")
    os.remove(temp_wav)

    return output_path


def check_for_updates(self):
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/Cypher-Monarch/Chrona/master/version/version.txt",
            timeout=5,
        )
        latest_version = response.text.strip()
        if latest_version != VERSION:
            QMessageBox.information(
                self,
                "Update Available",
                f"A new version {latest_version} is available! Please update for the latest features and fixes.",
            )
    except requests.RequestException as e:
        QMessageBox.warning(
            self,
            "Update Check Failed",
            f"Could not check for updates: {e}\nYou can manually check on GitHub.",
        )


class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text-to-Speech & MP3 Converter")
        self.setWindowIcon(QIcon("Chrona.png"))
        self.setFixedSize(480, 420)
        self.status_label = QLabel("Status: Waiting for file...", self)
        self.status_label.setWordWrap(True)
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

        self.status_label.setFixedHeight(100)

        # Voices list
        self.voices = engine.getProperty("voices")
        self.voice_id = self.voices[0].id

        # UI Elements
        self.label = QLabel("📄 Choose a file to convert", self)
        self.label.setStyleSheet("font-size: 16px;")

        self.voice_dropdown = QComboBox()
        for v in self.voices:
            self.voice_dropdown.addItem(v.name)
        self.voice_dropdown.currentIndexChanged.connect(self.change_voice)

        self.slider_label = QLabel("🔊 Speed: 150")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(80)
        self.speed_slider.setMaximum(250)
        self.speed_slider.setValue(150)
        self.speed_slider.valueChanged.connect(self.update_speed_label)

        self.speak_radio = QRadioButton("🗣️ Speak Only")
        self.mp3_radio = QRadioButton("🎵 MP3 Only")
        self.both_radio = QRadioButton("🔊 Speak + MP3")
        self.both_radio.setChecked(True)  # default

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.speak_radio)
        self.mode_group.addButton(self.mp3_radio)
        self.mode_group.addButton(self.both_radio)

        self.button = QPushButton("Browse File", self)
        self.button.clicked.connect(self.browse_file)

        # Layouts
        layout = QVBoxLayout()
        layout.addSpacing(10)
        layout.addWidget(self.label)
        layout.addSpacing(5)

        # Create container for advanced options
        self.advanced_options_container = QWidget()
        adv_layout = QHBoxLayout()
        adv_layout.addWidget(self.speak_radio)
        adv_layout.addWidget(self.mp3_radio)
        adv_layout.addWidget(self.both_radio)
        self.advanced_options_container.setLayout(adv_layout)

        # Initially hide the advanced options
        self.advanced_options_container.setVisible(False)

        # Create a toggle button for advanced options
        self.advanced_hint = QLabel("Advanced Options")
        self.advanced_hint.setAlignment(Qt.AlignRight)
        self.advanced_hint.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 12px;
                padding-right: 4px;
                text-decoration: underline;
            }
        """)
        self.advanced_hint.mousePressEvent = self.toggle_advanced_options

        # Add toggle button and container to main layout
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
        check_for_updates(self)

    def toggle_advanced_options(self, event=None):
        is_visible = self.advanced_options_container.isVisible()
        self.advanced_options_container.setVisible(not is_visible)
        if is_visible:
            self.advanced_hint.setText("▶ Advanced Options")
        else:
            self.advanced_hint.setText("▼ Advanced Options")

    def log(self, message):
        self.status_label.setText(message)

    def update_speed_label(self, value):
        self.slider_label.setText(f"🔊 Speed: {value}")

    def change_voice(self, index):
        self.voice_id = self.voices[index].id

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Documents (*.txt *.docx *.pdf)"
        )
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        reply = QMessageBox.question(
            self,
            "Confirm Conversion",
            "Are you sure you want to convert this file?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            self.log("⚠️ Conversion cancelled by user.")
            return
        try:
            if file_path.endswith(".docx"):
                text = read_word_file(file_path)
            elif file_path.endswith(".pdf"):
                text = read_pdf_file(file_path)
            elif file_path.endswith(".txt"):
                text = read_txt_file(file_path)
            else:
                self.log("❌ Unsupported file format!")
                return

            self.log("✅ File loaded. Processing...")

            rate = self.speed_slider.value()
            voice_id = self.voice_id
            volume = 1.0

            if self.speak_radio.isChecked():
                speak(text, rate, volume, voice_id)
                self.log("✅ Spoken aloud successfully!")

            elif self.mp3_radio.isChecked():
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                mp3_path = save_as_mp3(text, file_name, rate, volume, voice_id)
                self.log(f"✅ MP3 saved at:\n{mp3_path}")

            else:  # both
                speak(text, rate, volume, voice_id)
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                mp3_path = save_as_mp3(text, file_name, rate, volume, voice_id)
                self.log(f"✅ Spoken and MP3 saved at:\n{mp3_path}")

        except Exception as e:
            self.log(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("Chrona.png"))
    window = TTSApp()
    window.show()
    app.exec()
