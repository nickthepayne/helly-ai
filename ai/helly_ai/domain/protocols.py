from typing import List, Protocol, Optional
from pydantic import BaseModel

class FeedbackItem(BaseModel):
    id: str
    content: str
    created_at: str

class FeedbackRef(BaseModel):
    id: str
    created_at: str
    snippet: str

class VectorStore(Protocol):
    def upsert_member_corpus(self, member_id: str, items: List[FeedbackItem], time_range: Optional[tuple[str, str]] = None) -> None: ...
    def query(self, member_id: str, text: str, time_range: Optional[tuple[str, str]] = None, k: int = 10) -> List[FeedbackRef]: ...

class Embedder(Protocol):
    def embed_texts(self, texts: List[str]) -> List[List[float]]: ...

class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...

class QueryResponse(BaseModel):
    answer: str
    citations: List[FeedbackRef] | None = None
    meta: dict | None = None

class RAGPipeline(Protocol):
    def ingest(self, member_ref: str, items: List[FeedbackItem], time_range: Optional[tuple[str, str]] = None) -> None: ...
    def answer(self, question: str, time_range: Optional[tuple[str, str]] = None, person_hint: Optional[str] = None) -> QueryResponse: ...

