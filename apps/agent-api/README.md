# Enterprise Agent API — Days 1–3

Independent FastAPI service alongside the Next.js portfolio. This is **document ingestion**, NOT a completed RAG/LLM/AI Agent system.

## Run (local only, sample/non-sensitive data)
From apps/agent-api:

1. docker compose up --build -d
2. curl http://localhost:8000/health/live
3. curl http://localhost:8000/health/ready
4. curl -F 'file=@sample.md' http://localhost:8000/api/v1/documents

Open http://localhost:8000/docs to inspect the API contract.

## Scope
- Day 1: structure, service boundaries, upload contract and tests.
- Day 2: FastAPI liveness/readiness, PostgreSQL 16 + pgvector, Docker Compose and database initialization.
- Day 3: TXT/Markdown/PDF extraction, deterministic overlapping chunks, metadata and transactional persistence, duplicate detection by SHA-256.
- Day 4 (NOT IMPLEMENTED): embeddings, vector similarity retrieval, grounded LLM answers.

## Test
Install requirements-dev.txt and run: PYTHONPATH=. pytest -q

The 10 API/ingestion tests use SQLite; passing them does not prove PostgreSQL/pgvector integration. Docker integration must be run on a machine with Docker.

## Safety limitations
No authentication, tenant isolation, malware scanning or file access controls. Development only, localhost bindings only, no confidential uploads. Text is UTF-8; PDF requires extractable text, max 50 pages; max file size 5 MiB. The default database credentials are for isolated local use only. Add real secrets management and Alembic migrations before production.

The embedding VECTOR(1536) column is nullable by design; Day 4 must populate it with genuine embeddings and add search/index tests. No fabricated evaluation or performance metrics.
