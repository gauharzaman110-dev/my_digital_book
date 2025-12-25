from fastapi import APIRouter, HTTPException, status
from src.models.request_models import EmbedRequest, EmbedResponse
from src.services.embedding_service import embedding_service

router = APIRouter(prefix="/embed", tags=["embed"])


@router.post("/", response_model=EmbedResponse)
async def embed_book_content(
    request: EmbedRequest
):
    """
    Load and embed all book markdown files into the vector database.

    Args:
        request: EmbedRequest containing the path to book content

    Returns:
        EmbedResponse with status of the embedding process
    """
    try:
        result = embedding_service.process_and_embed_book_content(request.book_content_path)

        # Convert the result to EmbedResponse format
        response = EmbedResponse(
            status=result["status"],
            chunks_processed=result["chunks_processed"],
            message=result["message"]
        )

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding process failed: {str(e)}"
        )