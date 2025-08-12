# Helly AI (/ai)

API-only Python FastAPI service for ingestion and query with RAG abstractions.

Scope (MVP):
- Routers for /ingest/member-corpus and /query
- Protocols for VectorStore, Embedder, EntityResolver, RAGPipeline
- No concrete implementations
- No error handling

How to install deps:
- make install

How to run (npm-like):
- npm run dev

How to run tests (npm-like):
- npm run test

### Environment via .env

- Copy ai/.env.example to ai/.env and fill values. The AI app loads it automatically on startup.
- Existing environment variables take precedence over .env values.

Required:
- OPENROUTER_API_KEY
- OPENROUTER_MODEL (e.g., deepseek/deepseek-chat-v3-0324:free)

Optional:
- CHROMA_PERSIST_DIR (default .chroma)


