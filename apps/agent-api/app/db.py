"""SQLAlchemy entities for document ingestion and future vector retrieval."""
import os
from functools import lru_cache
from typing import Iterator
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.types import UserDefinedType

class Vector1536(UserDefinedType):
    """pgvector column placeholder for the Day 4 embedding step."""
    cache_ok = True
    def get_col_spec(self, **kw):
        return "VECTOR(1536)"

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector1536(), nullable=True)
    document: Mapped[Document] = relationship(back_populates="chunks")

@lru_cache(maxsize=1)
def engine():
    url = os.getenv("DATABASE_URL", "postgresql+psycopg://agent:agent_local@localhost:5432/agent")
    return create_engine(url, pool_pre_ping=True)

def get_db() -> Iterator[Session]:
    with Session(engine()) as session:
        yield session
