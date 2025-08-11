"""
OpenRouter-backed LLM client behind a swappable interface.

Requires env:
- OPENROUTER_API_KEY
- OPENROUTER_MODEL (e.g., `openrouter/auto` or a specific model)

Note: Uses the OpenAI-compatible SDK with a custom base_url.
This can be swapped to a direct OpenAI client by replacing base_url and the API key.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency not installed in scaffold
    OpenAI = None  # type: ignore

from helly_ai.domain.protocols import LLMClient


class OpenRouterLLMClient(LLMClient):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        if OpenAI is None:
            raise ImportError("openai package not installed. Install with `pip install openai`.\n"
                              "For OpenRouter, also set OPENROUTER_API_KEY and OPENROUTER_MODEL.")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def complete(self, prompt: str) -> str:
        # Minimal text completion using chat endpoint
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

