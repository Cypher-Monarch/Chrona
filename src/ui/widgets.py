from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSlider,
    QWidget,
)


def build_widgets(window) -> None:
    window.status_label = QLabel("Waiting for file...", window)
    window.status_label.setWordWrap(True)
    window.status_label.setFixedHeight(46)

    window.cancel_button = QPushButton("Cancel", window)
    window.cancel_button.setMinimumHeight(38)
    window.cancel_button.clicked.connect(window.cancel_audio)
    window.cancel_button.setVisible(False)

    window.label = QLabel("Choose a file to convert", window)
    window.label.setObjectName("titleLabel")

    window.voice_label = QLabel("Voice", window)
    window.voice_label.setObjectName("fieldLabel")

    window.voice_dropdown = QComboBox()
    for voice in window.voices:
        window.voice_dropdown.addItem(voice.name)
    window.voice_dropdown.currentIndexChanged.connect(window.change_voice)

    window.speed_value = QLabel("150", window)
    window.speed_value.setObjectName("speedValue")
    window.speed_value.setAlignment(Qt.AlignmentFlag.AlignRight)

    window.slider_label = QLabel("Speed", window)
    window.slider_label.setObjectName("fieldLabel")

    window.speed_slider = QSlider(Qt.Orientation.Horizontal)
    window.speed_slider.setMinimum(80)
    window.speed_slider.setMaximum(250)
    window.speed_slider.setValue(150)
    window.speed_slider.valueChanged.connect(window.update_speed_label)

    window.speak_radio = QRadioButton("Speak Only")
    window.mp3_radio = QRadioButton("MP3 Only")
    window.both_radio = QRadioButton("Speak + MP3")
    window.both_radio.setChecked(True)

    window.mode_group = QButtonGroup()
    window.mode_group.addButton(window.speak_radio)
    window.mode_group.addButton(window.mp3_radio)
    window.mode_group.addButton(window.both_radio)

    window.button = QPushButton("Browse File", window)
    window.button.setMinimumHeight(38)
    window.button.clicked.connect(window.browse_file)

    window.advanced_options_container = QWidget()

    advanced_layout = QHBoxLayout()
    advanced_layout.setContentsMargins(0, 2, 0, 2)
    advanced_layout.setSpacing(12)
    advanced_layout.addWidget(window.speak_radio)
    advanced_layout.addWidget(window.mp3_radio)
    advanced_layout.addWidget(window.both_radio)

    window.advanced_options_container.setLayout(advanced_layout)
    window.advanced_options_container.setVisible(False)

    window.advanced_hint = QLabel("▶ Advanced Options")
    window.advanced_hint.setAlignment(Qt.AlignmentFlag.AlignRight)
    window.advanced_hint.mousePressEvent = window.toggle_advanced_options
