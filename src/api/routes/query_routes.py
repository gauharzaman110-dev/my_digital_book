from fastapi import APIRouter, Depends, HTTPException, status
from src.models.request_models import QueryRequest, QueryResponse
from src.services.rag_service import rag_service
# from src.api.middleware import get_current_user

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
async def query_book_content(
    request: QueryRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Answer questions using RAG over the full book content.

    Args:
        request: QueryRequest containing the question and session ID
        # current_user: Current user (from auth middleware)

    Returns:
        QueryResponse with the answer and sources
    """
    try:
        result = rag_service.answer_question_with_rag(
            question=request.question,
            session_id=str(request.session_id)
        )

        # Convert the result to QueryResponse format
        response = QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=result["session_id"],
            mode_used=result["mode_used"]
        )

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query process failed: {str(e)}"
        )