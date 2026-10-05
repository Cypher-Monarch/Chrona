from PySide6.QtGui import QIcon

from constants import ICON_PATH


def build_window(window) -> None:
    window.setWindowTitle("Chrona")
    window.setWindowIcon(QIcon(str(ICON_PATH)))
    window.setFixedSize(460, 390)
