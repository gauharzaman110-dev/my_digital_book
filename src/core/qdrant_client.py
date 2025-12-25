# TEMPORARILY DISABLED — RAG WILL BE RESTORED LATER
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import VectorParams, Distance

from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class QdrantChatbotClient:
    def __init__(self, url: str, api_key: str):
        try:
            self.client = QdrantClient(url=url, api_key=api_key)
            self.collection_name = "document_chunks"
            self.embedding_dim = 768   # Gemini embeddings size
            self.is_available = True
            self._initialize_collection()
        except Exception as e:
            logger.error(f"Qdrant initialization failed: {e}")
            self.is_available = False
            raise e


    def _initialize_collection(self):
        from qdrant_client.http.exceptions import UnexpectedResponse

        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Qdrant collection '{self.collection_name}' created.")
        except UnexpectedResponse as e:
            if "already exists" in str(e):
                print(f"Qdrant collection '{self.collection_name}' already exists. Skipping creation.")
            else:
                raise

    def store_document_chunks(self, chunks: List[dict]):
        """
        Store document chunks in Qdrant.

        Args:
            chunks: List of dictionaries containing chunk data
                   Each dict should have: id, text_content, chapter_title, source_file, chunk_order, embedding_vector, book_version
        """
        if not self.is_available:
            logger.warning("Qdrant is not available. Skipping storage.")
            return

        points = []
        for chunk in chunks:
            point = models.PointStruct(
                id=str(chunk['id']),
                vector=chunk['embedding_vector'],
                payload={
                    "text_content": chunk['text_content'],
                    "chapter_title": chunk['chapter_title'],
                    "source_file": chunk['source_file'],
                    "chunk_order": chunk['chunk_order'],
                    "book_version": chunk['book_version']
                }
            )
            points.append(point)

        # Upload all points at once
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Stored {len(chunks)} document chunks in Qdrant")

    def search_similar_chunks(self, query_vector: List[float], limit: int = 5) -> List[dict]:
        """
        Search for similar document chunks to the query vector.

        Args:
            query_vector: The embedding vector to search for similarity
            limit: Maximum number of results to return

        Returns:
            List of dictionaries containing the similar chunks and their metadata
        """
        if not self.is_available:
            logger.warning("Qdrant is not available. Returning empty results.")
            return []

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        results = []
        for hit in search_result:
            chunk_data = {
                "id": hit.id,
                "text_content": hit.payload.get("text_content"),
                "chapter_title": hit.payload.get("chapter_title"),
                "source_file": hit.payload.get("source_file"),
                "chunk_order": hit.payload.get("chunk_order"),
                "book_version": hit.payload.get("book_version"),
                "score": hit.score
            }
            results.append(chunk_data)

        return results

    def delete_collection(self):
        """Delete the entire collection (useful for testing/refreshing data)."""
        self.client.delete_collection(self.collection_name)
        logger.info(f"Deleted collection '{self.collection_name}'")


# Global instance
qdrant_client = None


def init_qdrant_client(url: str, api_key: str):
    """Initialize the global Qdrant client instance."""
    global qdrant_client
    qdrant_client = QdrantChatbotClient(url, api_key)