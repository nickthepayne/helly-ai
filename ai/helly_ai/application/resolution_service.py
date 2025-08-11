from __future__ import annotations

from typing import List, Optional

from helly_ai.domain.resolution import ResolveCandidate, ResolveHit, ResolveResponse
from helly_ai.domain.protocols import LLMClient


class MemberResolutionService:
    """
    Stateless assistive member resolver powered by an LLM.
    Does not apply permissions; candidates are supplied by the caller (/app).
    """

    def __init__(self, llm: LLMClient):
        self._llm = llm

    def resolve(self, text: str, candidates: List[ResolveCandidate], context: Optional[str] = None) -> ResolveResponse:
        # Form a compact, deterministic prompt for ranking provided candidates.
        roster = "\n".join(
            f"- id:{c.id} name:{c.displayName}"
            + (f" emails:{','.join(c.emails or [])}" if c.emails else "")
            + (f" aliases:{','.join(c.aliases or [])}" if c.aliases else "")
            for c in candidates
        )
        system = (
            "You are a helpful assistant that selects the most likely person from a provided candidate list."
            " Only choose among the given candidates."
            " Return a concise JSON object with fields: topCandidate(id, score, rationale), alternatives[], confidence."
            " Scores should be between 0 and 1."
        )
        user = (
            f"Text: {text}\n"
            + (f"Context: {context}\n" if context else "")
            + f"Candidates:\n{roster}\n"
            + "Respond ONLY with JSON, no extra commentary."
        )
        prompt = f"System: {system}\nUser: {user}"
        raw = self._llm.complete(prompt)
        # For MVP: assume LLM returns valid JSON; robust parsing/validation can be added later.
        import json

        data = json.loads(raw)
        # Map into ResolveResponse, but be tolerant of missing fields (MVP leniency)
        top = data.get("topCandidate")
        alts = data.get("alternatives", []) or []
        resp = ResolveResponse(
            topCandidate=ResolveHit(**top) if top else None,
            alternatives=[ResolveHit(**a) for a in alts if a],
            confidence=data.get("confidence"),
        )
        return resp

