"""Chrona update checking."""

import requests
from PySide6.QtWidgets import QMessageBox

from constants import UPDATE_URL, VERSION


def check_for_updates(parent=None) -> None:
    """Check GitHub for a newer Chrona version."""
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        response.raise_for_status()

        latest_version = response.text.strip()

        if latest_version != VERSION:
            QMessageBox.information(
                parent,
                "Update Available",
                (
                    f"A new version {latest_version} is available! "
                    "Please update for the latest features and fixes."
                ),
            )
    except requests.RequestException as exc:
        QMessageBox.warning(
            parent,
            "Update Check Failed",
            (f"Could not check for updates: {exc}\nYou can manually check on GitHub."),
        )
