from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/v1")

class FeedbackItem(BaseModel):
    id: str
    content: str
    created_at: str

class FeedbackRef(BaseModel):
    id: str
    created_at: str
    snippet: str

class IngestRequest(BaseModel):
    team_member_ref: str
    items: List[FeedbackItem]
    from_: Optional[str] = None
    to: Optional[str] = None
    wipe_existing: bool = True

class QueryRequest(BaseModel):
    question: str
    from_: Optional[str] = None
    to: Optional[str] = None
    person_hint: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: Optional[List[FeedbackRef]] = None
    meta: Optional[dict] = None

@router.post("/ingest/member-corpus", status_code=202)
async def ingest_member_corpus(req: IngestRequest):
    raise NotImplementedError("MVP scaffold only")

@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    raise NotImplementedError("MVP scaffold only")

