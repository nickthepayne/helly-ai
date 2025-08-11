## Helly.ai – Agent Guide (Design, Best Practices, Rules)

This document captures the most important principles and patterns to follow for any future agent (or human) continuing work on Helly.ai.

### Purpose
- Build an API-only system that helps managers capture feedback and ask questions about team members.
- Prioritize clean interfaces and swappable implementations so components can evolve independently.

---

### High-Level Architecture
- Two services with strict boundaries:
  1) Software App (/app): Kotlin + Spring Boot
     - Owns identity, permissions, persistence, and business decisions
     - Exposes REST endpoints for team members, feedback, and asking questions
     - Calls AI service for RAG and for member disambiguation assistance (ranking), but remains the authority
  2) AI App (/ai): Python + FastAPI
     - Provides APIs for corpus ingestion, semantic query (RAG), and member resolution assistance (ranking among provided candidates)
     - Implements RAG abstractions and composition; no business authority

Separation of concerns is critical. The AI service must not make authoritative identity or permission decisions; it only assists.

---

### Ownership & Responsibilities
- /app owns:
  - Team roster, data persistence, feedback storage, and events
  - Identity mapping and permission checks
  - Final choice of memberId (after consulting AI for ranking)
- /ai owns:
  - Stateless RAG pipeline and vector search
  - LLM-powered ranking for member resolution among caller-provided candidates
  - Swappable infrastructure for LLM, embeddings, and vector DB

---

### Design Principles
- Interfaces first: define protocols/ports before implementations
- Swappability: every external dependency behind an interface
- API-first: define/update OpenAPI specs; align DTOs and controllers/routers accordingly
- Keep the API layer thin: no business logic in controllers/routers; move logic to services
- Testable composition: favor small factories/containers for wiring
- Minimalism for MVP: keep logic small; add TODOs where design choices may evolve

---

### Swappable Abstractions
- /ai (Python):
  - Embedder (default: SentenceTransformers)
  - VectorStore (default: Chroma)
  - LLMClient (default: OpenRouter using OpenAI-compatible SDK)
  - RAGPipeline (ingest, answer)
  - MemberResolutionService uses LLMClient to rank provided candidates
- /app (Kotlin):
  - Repositories (TeamMemberRepository, FeedbackRepository)
  - AiClient (ask, ingestAll)
  - EventPublisher
  - EntityResolutionService (app remains authority; if consulting AI, it passes candidates it is allowed to see)

---

### Current RAG Stack (local, free)
- Embeddings: SentenceTransformers (default: all-MiniLM-L6-v2)
- Vector DB: Chroma PersistentClient (local, per-member collections; can switch to shared collection with metadata filters later)
- LLM: OpenRouter (swappable to OpenAI or others)
- Composition in /ai via simple factories in helly_ai/application/container.py

---

### LLM & Resolution
- LLM calls are behind LLMClient; do not call vendor SDKs directly in services
- Member resolution:
  - AI endpoint: POST /v1/resolve/member accepts text + candidates[] and returns ranked results
  - /app provides candidates (already permission-filtered) and remains the authority to choose final memberId
  - Never let /ai infer IDs outside the provided candidate set

---

### API Contracts
- /app
  - POST /v1/team-members — create
  - POST /v1/feedback — body: { content, createdAt?, personHint? }
  - GET  /v1/feedback?memberId&from&to — list
  - POST /v1/ask — body: { text }
- /ai
  - POST /v1/ingest/member-corpus — replace/ingest a member’s corpus
  - POST /v1/query — body: { text, from?, to?, person_hint? } (pipeline uses text)
  - POST /v1/resolve/member — body: { text, candidates[], context? } (returns ranked candidates)
- Keep OpenAPI specs in docs/openapi; update when endpoints change.

---

### Testing Strategy
- Integration-first to validate API shapes and interactions
- /app
  - SpringBootTest with RANDOM_PORT to exercise controllers
  - AI client mocked in tests via @Primary bean
  - Readability: use helpers and a small DSL (AppClient) to express user journeys
- /ai
  - Pytest integration tests
  - Local embedding + vector store integration tests (downloads the model on first run)
  - For resolution and RAG, use fake/mocked LLM clients in tests when appropriate

Best practices for tests
- Prefer end-to-end flows (create member -> feedback -> ask)
- Favor human-readable helpers/DSL to keep tests narrative-oriented
- Keep network calls local (no external calls in CI); mock LLM where needed

---

### Coding Conventions
- Kotlin (app):
  - camelCase for DTOs and fields (e.g., createdAt, personHint, teamMemberId)
  - Thin controllers; use services and repositories
  - Gradle wrapper; Java 21
- Python (ai):
  - Pydantic v2 models; FastAPI routers thin; logic in services
  - Protocols for interfaces (typing.Protocol)
  - Keep composition in container.py; avoid wiring in routers

---

### Configuration & Environment
- /ai
  - OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL
  - SENTENCE_TRANSFORMER_MODEL (default: all-MiniLM-L6-v2)
  - CHROMA_PERSIST_DIR (default: .chroma)
- Do not hardcode secrets; use env vars

---

### Security & Data Boundaries
- /app is the source of truth for identity and permissions
- /ai must treat IDs as opaque; it cannot discover or infer unauthorized IDs
- For member resolution, /app supplies a pre-filtered candidate list and uses /ai only as a ranker

---

### Implementation Guidance (Next Agents)
- Before implementing logic, add/adjust interfaces and update OpenAPI specs
- Keep adapters swappable; inject via factories
- Avoid pushing business logic into API layers; keep it in services
- Write or update integration tests alongside changes; keep readability high via DSL/helpers
- Favor local, free defaults for experimentation (SentenceTransformers + Chroma), but keep the interface seam clear for production-grade replacements
- Keep events in mind (FeedbackCreated) for future async ingestion; the current MVP can call ingestion synchronously via a port

---

### Do / Don’t Checklist
- Do
  - Keep boundaries strict between /app and /ai
  - Update OpenAPI when contract changes
  - Add tests that read like user journeys; use AppClient DSL in /app tests
  - Hide vendors behind interfaces (LLMClient, VectorStore, Embedder, AiClient)
  - Use package managers (Gradle, pip/pyproject) for dependencies
- Don’t
  - Put identity/permission decisions in /ai
  - Hardcode vendor SDK usage inside services (use LLMClient instead)
  - Implement heavy error handling in MVP
  - Add business logic in controllers/routers

---

### Quick Pointers
- /app test DSL: app/src/test/kotlin/helly/app/testsupport/AppClient.kt
- /ai composition: ai/helly_ai/application/container.py
- RAG interfaces: ai/helly_ai/domain/protocols.py
- Member resolution models/service: ai/helly_ai/domain/resolution.py and ai/helly_ai/application/resolution_service.py
- OpenAPI specs: docs/openapi/app.yaml, docs/openapi/ai.yaml

This guide should keep future changes consistent, safe, and reviewable while preserving our ability to swap implementations as we iterate.

