from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class ResolveCandidate(BaseModel):
    id: str
    displayName: str
    emails: Optional[List[str]] = None
    aliases: Optional[List[str]] = None


class ResolveHit(BaseModel):
    id: str
    score: float
    rationale: Optional[str] = None


class ResolveResponse(BaseModel):
    topCandidate: Optional[ResolveHit] = None
    alternatives: List[ResolveHit] = []
    confidence: Optional[str] = None

