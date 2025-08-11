"""
Simple local vector store backed by ChromaDB (runs locally, free).
Uses per-member collections, enabling easy filtering by member_id.
Embeddings are supplied explicitly via an Embedder to keep concerns separate.
"""
from __future__ import annotations

import os
from typing import List, Optional

try:
    import chromadb  # type: ignore
except Exception:  # pragma: no cover
    chromadb = None  # type: ignore

from helly_ai.domain.protocols import VectorStore, FeedbackItem, FeedbackRef, Embedder


class ChromaVectorStore(VectorStore):
    def __init__(self, embedder: Embedder, persist_dir: Optional[str] = None):
        if chromadb is None:
            raise ImportError("chromadb not installed. `pip install chromadb`")
        self._embedder = embedder
        self._persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", ".chroma")
        self._client = chromadb.PersistentClient(path=self._persist_dir)

    def _collection(self, member_id: str):
        name = f"member_{member_id}"
        return self._client.get_or_create_collection(name)

    def upsert_member_corpus(self, member_id: str, items: List[FeedbackItem], time_range: Optional[tuple[str, str]] = None) -> None:
        col = self._collection(member_id)
        ids = [i.id for i in items]
        docs = [i.content for i in items]
        metas = [{"created_at": i.created_at} for i in items]
        embeddings = self._embedder.embed_texts(docs)
        col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)

    def query(self, member_id: str, text: str, time_range: Optional[tuple[str, str]] = None, k: int = 10) -> List[FeedbackRef]:
        col = self._collection(member_id)
        qvec = self._embedder.embed_texts([text])[0]
        # Note: we can add advanced metadata filters here (e.g., date/company/team) via the `where` parameter.
        res = col.query(query_embeddings=[qvec], n_results=k)
        results: List[FeedbackRef] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        for i, doc, meta in zip(ids, docs, metas):
            created_at = meta.get("created_at") if isinstance(meta, dict) else None
            results.append(FeedbackRef(id=str(i), created_at=str(created_at or ""), snippet=str(doc)))
        return results

