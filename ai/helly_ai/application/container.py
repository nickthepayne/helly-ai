"""
Very small composition root for wiring implementations.
Swappable components exposed via factory functions.
"""
from __future__ import annotations

import os
from typing import Optional, List, Tuple

from helly_ai.domain.protocols import (
    VectorStore,
    Embedder,
    LLMClient,
    RAGPipeline,
    FeedbackItem,
    FeedbackRef,
    QueryResponse,
)
from helly_ai.application.resolution_service import MemberResolutionService
from helly_ai.domain.resolution import ResolveCandidate, ResolveResponse, ResolveHit

# Implementations
try:
    from helly_ai.infrastructure.vectorstores.chroma_store import ChromaVectorStore
except Exception:  # pragma: no cover
    ChromaVectorStore = None  # type: ignore

try:
    from helly_ai.infrastructure.embeddings.sentence_transformer import LocalSentenceTransformerEmbedder
except Exception:  # pragma: no cover
    LocalSentenceTransformerEmbedder = None  # type: ignore

try:
    from helly_ai.infrastructure.llm.openrouter_client import OpenRouterLLMClient
except Exception:  # pragma: no cover
    OpenRouterLLMClient = None  # type: ignore


def make_embedder() -> Embedder:
    if LocalSentenceTransformerEmbedder is None:
        # Dev fallback: no-op embedder
        class _DummyEmb(Embedder):
            def embed_texts(self, texts: List[str]) -> List[List[float]]:
                return [[0.0] * 3 for _ in texts]
        return _DummyEmb()  # type: ignore[return-value]
    model = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
    return LocalSentenceTransformerEmbedder(model)


def make_vector_store(embedder: Embedder | None = None) -> VectorStore:
    if ChromaVectorStore is None:
        # Dev fallback: in-memory vector store that returns last 0 citations
        class _DummyVS(VectorStore):
            def upsert_member_corpus(self, member_id: str, items: List[FeedbackItem], time_range: Optional[tuple[str, str]] = None) -> None:
                pass
            def query(self, member_id: str, text: str, time_range: Optional[tuple[str, str]] = None, k: int = 10) -> List[FeedbackRef]:
                return []
        return _DummyVS()  # type: ignore[return-value]
    emb = embedder or make_embedder()
    persist = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
    return ChromaVectorStore(embedder=emb, persist_dir=persist)


def make_llm_client() -> LLMClient:
    if OpenRouterLLMClient is None:
        # Dev fallback: canned text
        class _DummyLLM(LLMClient):
            def complete(self, prompt: str) -> str:
                return "[dev] mock answer"
        return _DummyLLM()  # type: ignore[return-value]
    return OpenRouterLLMClient()


class DefaultRAGPipeline(RAGPipeline):
    def __init__(self, vector_store: VectorStore, embedder: Embedder, llm: LLMClient):
        self._vs = vector_store
        self._emb = embedder
        self._llm = llm

    def ingest(self, member_ref: str, items: List[FeedbackItem], time_range: Optional[Tuple[Optional[str], Optional[str]]] = None) -> None:
        # For MVP: assume member_ref is already a concrete member_id
        self._vs.upsert_member_corpus(member_id=member_ref, items=items, time_range=time_range)

    def answer(
        self,
        question: str,
        time_range: Optional[Tuple[Optional[str], Optional[str]]] = None,
        person_hint: Optional[str] = None,
    ) -> QueryResponse:
        # For MVP: person_hint is the member_id. Entity resolution can be added later.
        member_id = person_hint or "unknown"
        citations: List[FeedbackRef] = self._vs.query(member_id=member_id, text=question, time_range=time_range, k=5)
        context = "\n".join(f"- {c.snippet}" for c in citations)
        prompt = f"Question: {question}\nContext:\n{context}"
        answer = self._llm.complete(prompt)
        return QueryResponse(answer=answer, citations=citations, meta={"member_id": member_id})


def make_rag_pipeline() -> RAGPipeline:
    emb = make_embedder()
    return DefaultRAGPipeline(make_vector_store(emb), emb, make_llm_client())  # type: ignore[return-value]


def make_rag_pipeline_with(
    llm: Optional[LLMClient] = None,
    embedder: Optional[Embedder] = None,
    vector_store: Optional[VectorStore] = None,
) -> RAGPipeline:
    emb = embedder or make_embedder()
    vs = vector_store or make_vector_store(emb)
    llm_client = llm or make_llm_client()
    return DefaultRAGPipeline(vs, emb, llm_client)  # type: ignore[return-value]

# Member resolution factory (assistive; app remains the authority)

def make_member_resolution_service(llm: Optional[LLMClient] = None) -> MemberResolutionService:
    return MemberResolutionService(llm or make_llm_client())


