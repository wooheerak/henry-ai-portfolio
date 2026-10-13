"""Days 1–3 API. This version intentionally does not call an LLM."""
import hashlib
from pathlib import PurePath
from uuid import uuid4
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db import Document, Chunk, get_db
from app.ingest import MAX_BYTES, extract_text, chunk_text

app = FastAPI(title="Enterprise Knowledge & Operations Agent", version="0.1.0")

class DocumentInfo(BaseModel):
    id: str
    filename: str
    content_type: str
    sha256: str
    chunk_count: int
    duplicate: bool = False

def present(doc: Document, duplicate: bool = False) -> DocumentInfo:
    return DocumentInfo(id=doc.id, filename=doc.filename, content_type=doc.content_type,
                        sha256=doc.sha256, chunk_count=doc.chunk_count, duplicate=duplicate)

@app.get("/health/live")
def live():
    return {"status": "ok", "service": "agent-api"}

@app.get("/health/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        ext = db.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")).scalar_one()
        if not ext:
            raise RuntimeError("pgvector extension is missing")
        return {"status": "ready", "database": "ok", "pgvector": "ok"}
    except Exception as exc:
        raise HTTPException(503, "Database or pgvector not ready") from exc

@app.post("/api/v1/documents", response_model=DocumentInfo, status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = PurePath((file.filename or "").replace("\\", "/")).name
    if not filename or len(filename) > 255:
        raise HTTPException(422, "Valid filename required")
    payload = await file.read(MAX_BYTES + 1)
    plain_text, media_type = extract_text(filename, payload)
    sha = hashlib.sha256(payload).hexdigest()
    existing = db.scalar(select(Document).where(Document.sha256 == sha))
    if existing:
        return present(existing, duplicate=True)
    parts = chunk_text(plain_text)
    doc = Document(id=str(uuid4()), filename=filename, content_type=media_type, sha256=sha, chunk_count=len(parts))
    doc.chunks = [Chunk(id=str(uuid4()), ordinal=i, content=part) for i, part in enumerate(parts)]
    db.add(doc)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        existing = db.scalar(select(Document).where(Document.sha256 == sha))
        if existing:
            return present(existing, duplicate=True)
        raise HTTPException(409, "Document insertion conflict") from exc
    db.refresh(doc)
    return present(doc)

@app.get("/api/v1/documents/{document_id}", response_model=DocumentInfo)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return present(doc)
