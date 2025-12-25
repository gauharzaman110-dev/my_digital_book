from fastapi import APIRouter, Depends, HTTPException, status
from src.models.request_models import SelectedTextRequest, QueryResponse
from src.services.selected_text_service import selected_text_service
# from src.api.middleware import get_current_user

router = APIRouter(prefix="/selected-text", tags=["selected-text"])


@router.post("/", response_model=QueryResponse)
async def answer_from_selected_text(
    request: SelectedTextRequest,
    # current_user: dict = Depends(get_current_user)
):
    """
    Answer questions using user-provided selected text.
    This endpoint bypasses vector search and generates responses exclusively from the provided text.

    Args:
        request: SelectedTextRequest containing the question, selected text and session ID
        # current_user: Current user (from auth middleware)

    Returns:
        QueryResponse with the answer (sources will be empty in selected-text mode)
    """
    try:
        result = selected_text_service.answer_from_selected_text(
            question=request.question,
            selected_text=request.selected_text,
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
            detail=f"Selected-text processing failed: {str(e)}"
        )