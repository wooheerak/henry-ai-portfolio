"""Text/PDF extraction with strict size and format limits."""
import io
from pathlib import Path
from fastapi import HTTPException
from pypdf import PdfReader

ALLOWED = {".txt": "text/plain", ".md": "text/markdown", ".pdf": "application/pdf"}
MAX_BYTES = 5 * 1024 * 1024
MAX_PAGES = 50

def extract_text(filename: str, content: bytes) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(415, "Only .txt, .md and .pdf are supported")
    if not content:
        raise HTTPException(422, "File is empty")
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "Maximum upload size is 5 MiB")
    if suffix == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            if reader.is_encrypted:
                raise HTTPException(422, "Encrypted PDFs are not supported")
            if len(reader.pages) > MAX_PAGES:
                raise HTTPException(413, "Maximum PDF length is 50 pages")
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(422, "PDF could not be parsed") from exc
    else:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(422, "Text must be UTF-8 encoded") from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise HTTPException(422, "No extractable text found")
    return text, ALLOWED[suffix]

def chunk_text(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    if not (size > 0 and 0 <= overlap < size):
        raise ValueError("Invalid chunk size or overlap")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        part = text[start:end].strip()
        if part:
            chunks.append(part)
        if end == len(text):
            break
        start = end - overlap
    return chunks
