import os
from pathlib import Path

import pytest

from helly_ai.infrastructure.embeddings.sentence_transformer import (
    LocalSentenceTransformerEmbedder,
)
from helly_ai.infrastructure.vectorstores.chroma_store import ChromaVectorStore
from helly_ai.domain.protocols import FeedbackItem


@pytest.mark.integration
def test_embedding_and_search_roundtrip(tmp_path: Path):
    """
    End-to-end local test:
    - Build embeddings with SentenceTransformers
    - Upsert into Chroma for two different members (Max and Lisa)
    - Query only Max's collection and ensure results are relevant to Max/API and do not leak Lisa's docs
    """
    # Arrange: local, free components
    persist_dir = tmp_path / ".chroma"
    embedder = LocalSentenceTransformerEmbedder(model_name=os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2"))
    store = ChromaVectorStore(embedder=embedder, persist_dir=str(persist_dir))

    max_member_id = "max-123"
    lisa_member_id = "lisa-456"

    max_corpus = [
        FeedbackItem(id="m1", content="Max improved the API performance significantly.", created_at="2024-06-01T10:00:00Z"),
        FeedbackItem(id="m2", content="Max struggled with communication in Q2 but got better by July.", created_at="2024-07-20T09:30:00Z"),
    ]

    lisa_corpus = [
        FeedbackItem(id="l1", content="Lisa organized an excellent team offsite in June.", created_at="2024-06-15T12:00:00Z"),
    ]

    # Act: upsert embeddings for both members
    store.upsert_member_corpus(member_id=max_member_id, items=max_corpus)
    store.upsert_member_corpus(member_id=lisa_member_id, items=lisa_corpus)

    # Query only Max's collection
    query_text = "How did Max do with API speed?"
    results = store.query(member_id=max_member_id, text=query_text, k=3)

    # Show results for visibility
    print("Retrieved IDs:", [r.id for r in results])
    for r in results:
        print("-", r.created_at, "|", r.snippet)

    # Assert: we retrieve relevant result(s) and do not see Lisa's doc id
    assert len(results) >= 1
    ids = {r.id for r in results}
    assert "l1" not in ids
    joined_snippets = "\n".join(r.snippet for r in results)
    assert ("api" in joined_snippets.lower()) or ("performance" in joined_snippets.lower())

    # Note: We can extend this later with metadata filters (e.g., date ranges) using Chroma `where` param.

