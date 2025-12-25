from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
import uuid
from src.services.agent_service import agent_service

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest
):
    """
    Chat endpoint that accepts a message and responds using the RAG system.
    Creates a new session if no session_id is provided.

    Args:
        request: ChatRequest containing the message and optional session_id

    Returns:
        ChatResponse with the response and session_id
    """
    try:
        # Generate a new session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Prepare data for the agent service
        request_data = {
            "question": request.message,
            "session_id": session_id
        }

        # Process the request using the agent service
        result = agent_service.process_user_request(request_data)

        # Return the response with the session ID
        return ChatResponse(
            response=result["answer"],
            session_id=result["session_id"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )