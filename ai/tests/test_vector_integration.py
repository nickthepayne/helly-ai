import os
from pathlib import Path

import pytest

from helly_ai.application.container import make_rag_pipeline_with
from helly_ai.domain.protocols import FeedbackItem, LLMClient


class CapturingFakeLLM(LLMClient):
    def __init__(self, canned: str = "Mocked answer") -> None:
        self.canned = canned
        self.last_prompt: str | None = None

    def complete(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.canned


@pytest.mark.integration
def test_end_to_end_rag_with_mock_llm(tmp_path: Path):
    """
    Single end-to-end test:
    1) Insert a corpus for two members (Max & Lisa)
    2) Ask a question about Max
    Assertions:
      - LLM receives a prompt containing relevant context (API/performance)
      - Citations are from Max only
    """
    # Build a pipeline with real local components and a mock LLM
    # Use a temp persist dir to keep test isolated
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path / ".chroma")
    fake_llm = CapturingFakeLLM(canned="Discuss API performance improvements with Max.")
    pipeline = make_rag_pipeline_with(llm=fake_llm)

    max_member_id = "max-123"
    lisa_member_id = "lisa-456"

    max_corpus = [
        FeedbackItem(id="m1", content="Max improved the API performance significantly.", created_at="2024-06-01T10:00:00Z"),
        FeedbackItem(id="m2", content="Max struggled with communication in Q2 but got better by July.", created_at="2024-07-20T09:30:00Z"),
    ]
    lisa_corpus = [
        FeedbackItem(id="l1", content="Lisa organized an excellent team offsite in June.", created_at="2024-06-15T12:00:00Z"),
    ]

    # 1) Insert corpus
    pipeline.ingest(member_ref=max_member_id, items=max_corpus)
    pipeline.ingest(member_ref=lisa_member_id, items=lisa_corpus)

    # 2) Ask a question
    question = "What should I discuss with Max tomorrow regarding performance?"
    resp = pipeline.answer(question=question, person_hint=max_member_id)

    # Surface outputs for visibility
    print("Answer:", resp.answer)
    print("Citations:", [c.id for c in resp.citations or []])
    for c in resp.citations or []:
        print("-", c.created_at, "|", c.snippet)

    # Assertions on LLM prompt content
    assert fake_llm.last_prompt is not None
    lower_prompt = fake_llm.last_prompt.lower()
    assert "context:" in lower_prompt
    assert "api" in lower_prompt or "performance" in lower_prompt

    # Assertions on citations belonging to the right member
    assert all(c.id.startswith("m") for c in resp.citations or [])

    # Mocked answer is returned
    assert "Discuss API performance" in resp.answer

