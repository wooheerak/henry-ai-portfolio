CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    sha256 VARCHAR(64) NOT NULL UNIQUE,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS chunks (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    UNIQUE (document_id, ordinal)
);
CREATE INDEX IF NOT EXISTS ix_chunks_document_id ON chunks(document_id);
