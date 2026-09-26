"""Chrona application entry point."""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import TTSApp


def main() -> None:
    app = QApplication([])
    app.setWindowIcon(QIcon("Chrona.png"))

    window = TTSApp()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
