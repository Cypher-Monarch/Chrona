"""Chrona Qt styles."""

APP_STYLE = """
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
        combobox-popup: 0;
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
"""

STATUS_STYLE = """
    QLabel {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        padding: 8px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 13px;
        color: #FFD700;
    }
"""

ADVANCED_HINT_STYLE = """
    QLabel {
        color: #FFD700;
        font-size: 12px;
        padding-right: 4px;
        text-decoration: underline;
    }
"""
