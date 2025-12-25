from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


# Request Models
class EmbedRequest(BaseModel):
    book_content_path: str


class EmbedResponse(BaseModel):
    status: str  # Enum [success, error]
    chunks_processed: int
    message: str


class QueryRequest(BaseModel):
    question: str
    session_id: UUID


class SelectedTextRequest(BaseModel):
    question: str
    selected_text: str
    session_id: UUID


# Response Models
class Source(BaseModel):
    chapter_title: str
    source_file: str
    text_preview: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]  # List of sources with chapter_title, source_file, text_preview
    session_id: UUID
    mode_used: str  # Enum [RAG, SELECTED_TEXT]