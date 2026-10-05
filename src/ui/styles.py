# Chrona Qt styles.

APP_STYLE = """
    QWidget {
        background-color: #0D0D0D;
        color: #E8E8E8;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 14px;
    }

    QLabel {
        color: #D6D6D6;
    }

    QLabel#titleLabel {
        color: #F0F0F0;
        font-size: 15px;
        font-weight: bold;
    }

    QLabel#fieldLabel {
        color: #8F8F8F;
        font-size: 12px;
    }

    QLabel#speedValue {
        color: #D6D6D6;
        font-size: 13px;
    }

    QComboBox {
        background-color: #171717;
        color: #E8E8E8;
        padding: 7px 10px;
        border: 1px solid #383838;
        border-radius: 8px;
        min-height: 20px;
        combobox-popup: 0;
    }

    QComboBox:hover {
        border-color: #555555;
    }

    QComboBox:focus {
        border-color: #FFD700;
    }

    QComboBox::drop-down {
        width: 30px;
        border: none;
    }

    QComboBox QAbstractItemView {
        background-color: #171717;
        color: #E8E8E8;
        border: 1px solid #383838;
        border-radius: 6px;
        padding: 4px;
        selection-background-color: #FFD700;
        selection-color: #0D0D0D;
        outline: none;
    }

    QSlider::groove:horizontal {
        background: #292929;
        height: 4px;
        border-radius: 2px;
    }

    QSlider::sub-page:horizontal {
        background: #FFD700;
        height: 4px;
        border-radius: 2px;
    }

    QSlider::add-page:horizontal {
        background: #292929;
        height: 4px;
        border-radius: 2px;
    }

    QSlider::handle:horizontal {
        background: #FFD700;
        width: 12px;
        height: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }

    QSlider::handle:horizontal:hover {
        background: #FFE45C;
    }

    QRadioButton {
        color: #BDBDBD;
        spacing: 7px;
        padding: 4px 2px;
    }

    QRadioButton:hover {
        color: #E8E8E8;
    }

    QRadioButton::indicator {
        width: 13px;
        height: 13px;
        border: 1px solid #555555;
        border-radius: 7px;
        background-color: #171717;
    }

    QRadioButton::indicator:hover {
        border-color: #FFD700;
    }

    QRadioButton::indicator:checked {
        background-color: #FFD700;
        border-color: #FFD700;
    }

    QPushButton {
        background-color: #171717;
        color: #D6D6D6;
        border: 1px solid #454545;
        padding: 9px 14px;
        font-weight: bold;
        border-radius: 7px;
    }

    QPushButton:hover {
        background-color: #1D1D1D;
        color: #FFD700;
        border-color: #FFD700;
    }

    QPushButton:pressed {
        background-color: #FFD700;
        color: #0D0D0D;
        border-color: #FFD700;
    }

    QPushButton:focus {
        border-color: #FFD700;
    }
"""

STATUS_STYLE = """
    QLabel {
        background-color: #141414;
        color: #A8A8A8;
        border: 1px solid #2D2D2D;
        border-radius: 7px;
        padding: 8px 10px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 12px;
    }
"""

ADVANCED_HINT_STYLE = """
    QLabel {
        color: #777777;
        font-size: 12px;
        padding: 4px 2px;
    }

    QLabel:hover {
        color: #FFD700;
    }
"""
