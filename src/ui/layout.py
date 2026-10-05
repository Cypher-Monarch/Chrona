from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout


def build_layout(window) -> None:
    layout = QVBoxLayout()
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(0)

    layout.addWidget(window.label)
    layout.addSpacing(18)

    layout.addWidget(window.voice_label)
    layout.addSpacing(5)
    layout.addWidget(window.voice_dropdown)

    layout.addSpacing(16)

    speed_header = QHBoxLayout()
    speed_header.setContentsMargins(0, 0, 0, 0)
    speed_header.addWidget(window.slider_label)
    speed_header.addStretch()
    speed_header.addWidget(window.speed_value)
    layout.addLayout(speed_header)

    layout.addSpacing(7)
    layout.addWidget(window.speed_slider)

    layout.addSpacing(6)
    layout.addWidget(window.advanced_hint)
    layout.addWidget(window.advanced_options_container)

    layout.addSpacing(12)
    layout.addWidget(window.button)

    layout.addSpacing(12)
    layout.addWidget(window.status_label)

    layout.addSpacing(8)
    layout.addWidget(window.cancel_button)

    layout.addStretch()
    window.setLayout(layout)

    layout.addStretch()

    window.setLayout(layout)
