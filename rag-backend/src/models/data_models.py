from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID, uuid4


class Question(BaseModel):
    """A natural language query submitted by the user, containing the query text and metadata about the source and mode (RAG or selected-text)"""
    id: UUID = None
    text: str
    mode: str  # Enum ['RAG', 'SELECTED_TEXT']
    session_id: UUID
    timestamp: datetime = None
    source_metadata: Optional[dict] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = uuid4()
        if not self.timestamp:
            self.timestamp = datetime.now()


class DocumentChunk(BaseModel):
    """A segment of the book content with associated metadata including text content, chapter title, source file name, and embedding vector"""
    id: UUID = None
    text_content: str
    chapter_title: str
    source_file: str
    chunk_order: int
    embedding_vector: List[float]  # Array of Floats (The embedding vector for similarity search)
    book_version: str

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = uuid4()


class ChatSession(BaseModel):
    """A collection of interactions between a user and the chatbot, including questions asked, responses received, timestamps, and session metadata"""
    id: UUID = None
    user_id: Optional[UUID] = None  # Can be null for anonymous sessions
    session_start: datetime = None
    session_end: Optional[datetime] = None  # null if active
    metadata: Optional[dict] = None
    session_expiry: datetime  # When the session automatically expires based on retention policy

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = uuid4()
        if not self.session_start:
            self.session_start = datetime.now()


class QueryLog(BaseModel):
    """A record of each interaction with the system, including the input question, response generated, mode used (RAG vs selected-text), timestamp, and any relevant metrics"""
    id: UUID = None
    question_id: UUID
    response_text: str
    mode_used: str  # Enum ['RAG', 'SELECTED_TEXT']
    retrieved_chunks: List[UUID]  # References to Document Chunks used for RAG
    response_time_ms: int  # Time taken to generate the response in milliseconds
    timestamp: datetime = None
    user_satisfaction: Optional[int] = None  # Optional rating, 1-5 scale
    quality_metrics: Optional[dict] = None  # Metrics about the quality of the response, for observability

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = uuid4()
        if not self.timestamp:
            self.timestamp = datetime.now()