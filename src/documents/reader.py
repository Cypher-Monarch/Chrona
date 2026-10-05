# Document loading utilities.

from pathlib import Path

import docx
import PyPDF2


def read_word_file(file_path: str | Path) -> str:
    # Read paragraph text from a DOCX file.
    doc = docx.Document(str(file_path))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def read_pdf_file(file_path: str | Path) -> str:
    # Extract text from all pages of a PDF file.
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def read_txt_file(file_path: str | Path) -> str:
    # Read a UTF-8 text file.
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


READERS = {
    ".docx": read_word_file,
    ".pdf": read_pdf_file,
    ".txt": read_txt_file,
}


def read_document(file_path: str | Path) -> str:
    # Read a supported document based on its file extension.
    path = Path(file_path)
    reader = READERS.get(path.suffix.lower())

    if reader is None:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    return reader(path)
