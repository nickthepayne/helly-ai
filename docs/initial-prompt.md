## Helly.ai MVP — Design-First Agent Prompt (Interfaces & Abstractions Only)

You are an expert software architect and senior IC tasked with scaffolding the FIRST iteration of Helly.ai as specified in:
- docs/product-vision.md (strategic vision, agent model)
- docs/mvp.md (MVP product + tech spec)

Goal of this iteration: produce clear interfaces/abstractions, API contracts, schemas, directory structure, and test scaffolds ONLY. Do NOT implement business logic. This pass is for design review and architecture alignment.

---

### Scope
Create two separable applications with clean boundaries:
1) Software App (/app): Kotlin + Spring Boot + PostgreSQL
   - Expose REST API for teams, team members, feedback CRUD
   - Persist feedback
   - Forward “ask about a team member” questions to the AI app via HTTP
2) AI App (/ai): Python + FastAPI (API-only)
   - Endpoints for ingestion and query
   - Define RAG abstractions (vector store, embedder, pipeline) WITHOUT concrete implementations

Do not build a UI. Everything is API-only.

---

### Non-Goals (for this iteration)
- No business logic, no concrete integrations (Slack, HRIS, vector DB, LLM)
- No migrations beyond minimal schema stubs
- No auth/identity beyond placeholders
- No infra/deployment scripts beyond simple run instructions

---

### Architectural Principles
- API-first: Define OpenAPI specs and DTOs before code
- Separation of concerns and clean boundaries between /app and /ai
- Event-driven shape: model a FeedbackCreated event and an ingestion trigger (HTTP call), even if the first version uses a simple synchronous call
- Replaceable adapters: vector store and embedding providers must be behind interfaces/protocols
- Readable, minimal, testable scaffolds

---

### Deliverables (Checklist)
Provide these artifacts as code + docs, with TODOs and NotImplemented placeholders:
- Overall repository layout scaffold
- OpenAPI specs for both services
- Controller/route stubs, DTOs, validators, error models
- Domain model (entities/value objects) and repository/service interfaces
- Event model (FeedbackCreated) and an Application Port interface for publishing/handling
- AI app protocols: VectorStore, Embedder, RAGPipeline, IngestionService, QueryService
- Persistence interface definitions only (no DB code)
- Configuration placeholders and environment variable contract
- Integration test scaffolds for both services (API level; mock external calls)
- Minimal READMEs per service: how to run tests and start a dev server

---

### Repository Structure to Create
- /app (Kotlin, Spring Boot 3.x)
  - build.gradle.kts, settings.gradle.kts (placeholders ok)
  - src/main/kotlin/helly/app/
    - api/ (controllers)
    - application/ (use-cases, services, ports)
    - domain/ (entities, value objects, events)
    - infrastructure/ (adapters: http client to /ai only as interface + stub)
    - config/
  - src/main/resources/
  - src/test/kotlin/helly/app/ (integration tests)
- /ai (Python 3.11+, FastAPI)
  - pyproject.toml or requirements.txt (placeholders ok)
  - helly_ai/
    - api/ (routers)
    - application/ (services)
    - domain/ (models)
    - infrastructure/ (adapters interfaces only)
    - config/
  - tests/ (integration tests)
- /docs
  - initial-prompt.md (this file)
  - mvp.md, product-vision.md (given)

---

### Software App (/app) — API Contract (OpenAPI outline)
Base path: /v1

Team Members
- POST /team-members
  - Body: { name, role, relationship_to_manager, start_date }
  - Returns: TeamMemberDTO { id, ... }
- GET /team-members/{id}
- GET /team-members?search=

Feedback
- POST /feedback
  - Body: FeedbackCreateDTO { team_member_id, content, created_at? }
  - Behavior: persist; publish FeedbackCreated event; invoke AI ingestion sync endpoint for that member (through an application port; actual HTTP call stubbed)
  - Returns: FeedbackDTO { id, team_member_id, content, created_at }
- GET /feedback?team_member_id=&from=&to=

Ask (delegates to AI App)
- POST /team-members/{id}/ask
  - Body: AskDTO { question, from?, to? }
  - Returns: AskResponseDTO { answer, citations?: [FeedbackRef] }
  - Implementation: controller -> application port -> stubbed AiClient; do not call a real server

Error Model
- Problem+JSON style: { type, title, status, detail, instance }

DTOs (Kotlin data classes)
- TeamMemberDTO(id: UUID, name: String, role: String, relationshipToManager: String, startDate: LocalDate)
- FeedbackDTO(id: UUID, teamMemberId: UUID, content: String, createdAt: Instant)
- FeedbackCreateDTO(teamMemberId: UUID, content: String, createdAt: Instant?)
- AskDTO(question: String, from: Instant?, to: Instant?)
- AskResponseDTO(answer: String, citations: List<FeedbackRef>?)
- FeedbackRef(id: UUID, createdAt: Instant, snippet: String)

Domain Model (no JPA yet; simple classes/interfaces)
- TeamMember(id, name, role, relationshipToManager, startDate)
- Feedback(id, teamMemberId, content, createdAt)
- Event: FeedbackCreated(id, teamMemberId, createdAt)

Ports/Interfaces
- TeamMemberRepository, FeedbackRepository (CRUD method signatures only)
- AiClient (ask(teamMemberId, question, from?, to?) -> AskResponseDTO; ingestAll(teamMemberId, items))
- EventPublisher (publish(event: FeedbackCreated))
- Use-cases: FeedbackService.addFeedback(...), AskService.ask(...)

Testing (integration scaffolds)
- SpringBootTest with MockMvc/WebTestClient
- Tests cover: create member -> add feedback -> POST ask (AiClient mocked)
- External calls mocked via a TestConfiguration bean

---

### AI App (/ai) — API Contract (OpenAPI outline)
Base path: /v1

Ingestion
- POST /ingest/member-corpus
  - Body: IngestRequest { team_member_id: UUID, items: [FeedbackItem], from?: Instant, to?: Instant, wipe_existing: true }
  - Semantics: replace existing corpus for member (MVP behavior)
  - Response: 202 Accepted + operation id

Query
- POST /query
  - Body: QueryRequest { team_member_id: UUID, question: String, from?: Instant, to?: Instant }
  - Response: QueryResponse { answer: String, citations: [FeedbackRef], meta?: { used_filters } }

Models
- FeedbackItem(id: UUID, content: String, created_at: Instant)
- FeedbackRef(id: UUID, created_at: Instant, snippet: String)

Abstractions/Protocols (Python typing.Protocol or ABC)
- VectorStore
  - upsert_member_corpus(member_id: UUID, items: list[FeedbackItem], time_range?: (from, to)) -> None
  - query(member_id: UUID, text: str, time_range?: (from, to), k: int=10) -> list[FeedbackRef]
- Embedder
  - embed_texts(texts: list[str]) -> list[list[float]]
- RAGPipeline
  - ingest(member_id, items, time_range?) -> None
  - answer(member_id, question, time_range?) -> QueryResponse
- IngestionService, QueryService: orchestrate via the above interfaces

Filtering Strategy (design only)
- Namespacing by team_member_id; time filters applied at query-time and/or precomputed shard keys; do not choose a concrete DB now

Testing (integration scaffolds)
- FastAPI TestClient (pytest) calling /ingest/member-corpus and /query
- Provide fake/no-op implementations that raise NotImplementedError to ensure design compile-time integrity only

---

### Events & Integration Flow (Design Only)
- On POST /feedback in /app: emit FeedbackCreated; application layer schedules/requests ingestion by calling AI App /ingest/member-corpus for that member (port method). Keep the call behind an interface; provide a stub implementation returning a fixed placeholder.

---

### Conventions & Guardrails
- Kotlin 1.9+, Spring Boot 3.x; Python 3.11, FastAPI, Pydantic v2
- Use clear package/module naming as shown above
- All non-trivial methods contain TODO and throw UnsupportedOperationException (Kotlin) or raise NotImplementedError (Python)
- No external network calls in tests
- Favor clean code and readability; keep files small and cohesive

---

### Output Expectations
Submit a PR-ready scaffold with:
- The directory structure and files
- OpenAPI specs (YAML) for both services
- Source files with interfaces, DTOs, controllers/routers stubs, and comments
- Test folders with 1–2 integration test skeletons per service
- README.md in /app and /ai explaining how to run tests and servers locally

Stop here. Do NOT implement business logic or concrete adapters. Surface any design questions as TODOs at top of relevant files.
