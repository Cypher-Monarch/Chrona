from PySide6.QtGui import QIcon


def build_window(window) -> None:
    window.setWindowTitle("Text-to-Speech & MP3 Converter")
    window.setWindowIcon(QIcon("Chrona.png"))
    window.setFixedSize(480, 420)
