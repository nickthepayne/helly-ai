from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from helly_ai.application.container import make_rag_pipeline
from helly_ai.domain.protocols import FeedbackItem, QueryResponse

router = APIRouter(prefix="/v1")
_pipeline = make_rag_pipeline()

class IngestRequest(BaseModel):
    team_member_ref: str
    items: List[FeedbackItem]
    from_: Optional[str] = None
    to: Optional[str] = None
    wipe_existing: bool = True

class QueryRequest(BaseModel):
    text: str
    from_: Optional[str] = None
    to: Optional[str] = None
    person_hint: Optional[str] = None

@router.post("/ingest/member-corpus", status_code=202)
async def ingest_member_corpus(req: IngestRequest):
    _pipeline.ingest(member_ref=req.team_member_ref, items=req.items, time_range=(req.from_, req.to))
    return {"status": "accepted"}

@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    return _pipeline.answer(question=req.text, time_range=(req.from_, req.to), person_hint=req.person_hint)

class ResolveCandidate(BaseModel):
    id: str
    displayName: str
    emails: Optional[List[str]] = None
    aliases: Optional[List[str]] = None

class ResolveRequest(BaseModel):
    text: str
    candidates: List[ResolveCandidate]
    context: Optional[str] = None

class ResolveHit(BaseModel):
    id: str
    score: float
    rationale: Optional[str] = None

class ResolveResponse(BaseModel):
    topCandidate: Optional[ResolveHit] = None
    alternatives: List[ResolveHit] = []
    confidence: Optional[str] = None

@router.post("/resolve/member", response_model=ResolveResponse)
async def resolve_member(req: ResolveRequest):
    # MVP: simple heuristic stub; replace with LLM later
    hits: List[ResolveHit] = []
    q = req.text.lower()
    for c in req.candidates:
        name = c.displayName.lower()
        score = 0.0
        if name and any(part in q for part in name.split()):
            score += 0.6
        if c.aliases:
            if any(a.lower() in q for a in c.aliases):
                score += 0.3
        if c.emails:
            if any(e.split("@")[0].lower() in q for e in c.emails):
                score += 0.2
        if score > 0:
            hits.append(ResolveHit(id=c.id, score=min(score, 1.0), rationale="heuristic"))
    hits.sort(key=lambda h: h.score, reverse=True)
    top = hits[0] if hits else None
    conf = "high" if top and top.score >= 0.8 else ("medium" if top and top.score >= 0.5 else "low")
    return ResolveResponse(topCandidate=top, alternatives=hits[1:], confidence=conf)


