"""Application configuration and filesystem paths."""

from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "Chrona"

DOCUMENTS_FOLDER = Path.home() / "Documents" / "Chrona"
ICON_PATH = Path("assets/c  hrona.png")

UPDATE_URL = (
    "https://raw.githubusercontent.com/Cypher-Monarch/Chrona/master/version/version.txt"
)
