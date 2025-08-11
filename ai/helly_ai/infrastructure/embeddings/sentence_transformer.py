"""
Local embeddings via SentenceTransformers (free to run locally).
Model is configurable via SENTENCE_TRANSFORMER_MODEL (defaults to 'all-MiniLM-L6-v2').
"""
from __future__ import annotations

import os
from typing import List

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - optional dep
    SentenceTransformer = None  # type: ignore

from helly_ai.domain.protocols import Embedder


class LocalSentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name: str | None = None):
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers not installed. `pip install sentence-transformers`")
        name = model_name or os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
        self._model = SentenceTransformer(name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        vectors = self._model.encode(texts, convert_to_numpy=True)
        return [v.tolist() for v in vectors]

