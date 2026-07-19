from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500, 
                         description="Pertanyaan seputar kebijakan NusantaraCare")
    mode: Literal["rag", "agentic"] = Field(default="rag", 
                                           description="Mode pemrosesan: rag (default) atau agentic")

class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    section_title: str

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    trace_id: str
    confidence_label: Literal["high", "medium", "low"]
    reason_code: Literal[
        "answered", 
        "no_relevant_context", 
        "conflicting_sources"
    ]

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    components: dict