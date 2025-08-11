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

