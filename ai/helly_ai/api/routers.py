from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import logging

from helly_ai.application.container import make_rag_pipeline, make_member_resolution_service
from helly_ai.domain.protocols import FeedbackItem, QueryResponse
from helly_ai.domain.resolution import ResolveCandidate, ResolveResponse

logger = logging.getLogger("helly_ai.api")

router = APIRouter(prefix="/v1")
_pipeline = make_rag_pipeline()
_resolver = make_member_resolution_service()
logger.info("RAG pipeline and resolver initialized")

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
    logger.info("/ingest/member-corpus member_ref=%s items=%d", req.team_member_ref, len(req.items))
    _pipeline.ingest(member_ref=req.team_member_ref, items=req.items, time_range=(req.from_, req.to))
    return {"status": "accepted"}

@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    logger.info("/query text_len=%d person_hint=%s", len(req.text or ""), req.person_hint)
    return _pipeline.answer(question=req.text, time_range=(req.from_, req.to), person_hint=req.person_hint)

class ResolveRequest(BaseModel):
    text: str
    candidates: Optional[List[ResolveCandidate]] = None
    context: Optional[str] = None


@router.post("/resolve/member", response_model=ResolveResponse)
async def resolve_member(req: ResolveRequest):
    logger.info("/resolve/member candidates=%d", len(req.candidates or []))
    return _resolver.resolve(text=req.text, candidates=req.candidates, context=req.context)


