import re
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

MAX_FILE_BYTES = 10 * 1024 * 1024
SUPPORTED = {".pdf", ".docx", ".txt", ".md"}


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError("Only PDF, DOCX, TXT, and MD files are supported.")
    if not content or len(content) > MAX_FILE_BYTES:
        raise ValueError("File must be non-empty and no larger than 10 MB.")
    if suffix == ".pdf":
        text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
    elif suffix == ".docx":
        document = Document(BytesIO(content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        text = content.decode("utf-8-sig")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError("No extractable text found in this document.")
    return text


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0.")
    words, chunks, start = text.split(), [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks
