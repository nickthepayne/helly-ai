"""
Very small composition root for wiring implementations.
Swappable components exposed via factory functions.
"""
from __future__ import annotations

import os
from typing import Optional

from helly_ai.domain.protocols import VectorStore, Embedder, EntityResolver, LLMClient, RAGPipeline

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


def make_vector_store() -> VectorStore:
    if ChromaVectorStore is None:
        raise RuntimeError("ChromaVectorStore not available; install 'chromadb'.")
    persist = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
    return ChromaVectorStore(persist)


def make_embedder() -> Embedder:
    if LocalSentenceTransformerEmbedder is None:
        raise RuntimeError("LocalSentenceTransformerEmbedder not available; install 'sentence-transformers'.")
    model = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
    return LocalSentenceTransformerEmbedder(model)


def make_llm_client() -> LLMClient:
    if OpenRouterLLMClient is None:
        raise RuntimeError("OpenRouterLLMClient not available; install 'openai'.")
    return OpenRouterLLMClient()


class DefaultRAGPipeline:
    def __init__(self, vector_store: VectorStore, embedder: Embedder, llm: LLMClient):
        self._vs = vector_store
        self._emb = embedder
        self._llm = llm

    # Placeholder methods; real logic to be implemented later
    def ingest(self, member_ref, items, time_range=None):  # type: ignore[no-redef]
        raise NotImplementedError

    def answer(self, question, time_range=None, person_hint=None):  # type: ignore[no-redef]
        raise NotImplementedError


def make_rag_pipeline() -> RAGPipeline:
    return DefaultRAGPipeline(make_vector_store(), make_embedder(), make_llm_client())  # type: ignore[return-value]

