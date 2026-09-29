"""Text normalization utilities."""

import re

from constants import MAX_SYNTHESIS_CHARS


def normalize_text(text: str) -> str:
    """Normalize extracted document text for further processing."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    """Split normalized text into non-empty paragraphs."""
    return [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]


def split_synthesis_chunks(
    paragraph: str,
    max_chars: int = MAX_SYNTHESIS_CHARS,
) -> list[str]:
    """Split a paragraph into bounded whitespace-separated chunks."""
    words = paragraph.split()
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for word in words:
        added_length = len(word) if not current else len(word) + 1

        if current and current_length + added_length > max_chars:
            chunks.append(" ".join(current))
            current = [word]
            current_length = len(word)
        else:
            current.append(word)
            current_length += added_length

    if current:
        chunks.append(" ".join(current))

    return chunks
