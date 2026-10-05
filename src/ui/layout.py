from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout


def build_layout(window) -> None:
    layout = QVBoxLayout()
    layout.addSpacing(10)
    layout.addWidget(window.label)
    layout.addSpacing(5)

    voice_layout = QHBoxLayout()
    voice_layout.addWidget(QLabel("🎤 Voice:"))
    voice_layout.addWidget(window.voice_dropdown)
    layout.addLayout(voice_layout)

    layout.addWidget(window.slider_label)
    layout.addWidget(window.speed_slider)
    layout.addWidget(window.advanced_hint)
    layout.addWidget(window.advanced_options_container)
    layout.addWidget(window.button)
    layout.addWidget(window.status_label)

    window.setLayout(layout)
